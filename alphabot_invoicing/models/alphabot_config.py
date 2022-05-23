# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError, Warning
import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    alphabot_fiscal_data = fields.Boolean(string="Campos impresora fiscal", config_parameter='account.move.alphabot_fiscal_data')
    alphabot_manual_printing = fields.Boolean(string='Botón impresión fiscal',
                                              config_parameter='account.move.alphabot_manual_printing')

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        params = self.env['ir.config_parameter'].sudo()
        params.set_param("alphabot_fiscal_data", self.alphabot_fiscal_data)
        params.set_param("alphabot_manual_printing", self.alphabot_manual_printing)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        _value = params.get_param("alphabot_fiscal_data", False)
        _value2 = params.get_param("alphabot_manual_printing", False)
        res.update(
            alphabot_fiscal_data=bool(_value),
            alphabot_manual_printing=bool(_value2)
        )
        return res


class AccountMove(models.Model):
    _inherit = "account.move"

    alphabot_estado = fields.Char(string="Estado imp. fiscal", size=1024, copy=False)
    alphabot_cliente_name = fields.Char(string="Cliente imp. fiscal", size=1024)
    alphabot_cliente_ruc = fields.Char(string="RUC imp. fiscal", size=1024)
    alphabot_devol_fact = fields.Char(string="Factura en Devol.", size=1024)

    alphabot_fiscal_data = fields.Boolean(compute='_compute_alphabot_settings', string='Campos para imp. fiscal ...')
    alphabot_manual_printing = fields.Boolean(compute='_compute_alphabot_settings', string='Botón impresión fiscal')

    def _compute_alphabot_settings(self):
        params = self.env['ir.config_parameter'].sudo()
        self.alphabot_fiscal_data = bool(params.get_param('account.move.alphabot_fiscal_data', default=False))
        self.alphabot_manual_printing = bool(params.get_param('account.move.alphabot_manual_printing', default=False))

    def _order_fields(self, vals):
        res = super(AccountMove, self)._order_fields(vals)
        res.update({
            'alphabot_estado': vals.get('alphabot_estado') or False,
            'alphabot_cliente_name': vals.get('alphabot_cliente_name') or False,
            'alphabot_cliente_ruc': vals.get('alphabot_cliente_ruc') or False,
            'alphabot_devol_fact': vals.get('alphabot_devol_fact') or False
        })
        return res

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        default['alphabot_estado'] = False
        default['narration'] = False
        return super(AccountMove, self).copy(default)

    def _reverse_moves(self, default_values_list=None, cancel=False):
        if not default_values_list:
            default_values_list = [{} for move in self]
        for move, default_values in zip(self, default_values_list):
            # Esto recupera el valor de la factura tipo TFBX110050782-00000693   
            sAux = False
            if type(move.alphabot_estado) == (str):
                if len(move.alphabot_estado) > 23:
                    sAux = move.alphabot_estado[-23:][0:22]
            default_values.update({
                'alphabot_devol_fact': sAux,
                'alphabot_estado': False,
                'narration': "",
            })
        return super(AccountMove, self)._reverse_moves(default_values_list, cancel)

    def action_print_fiscal(self):
        _logger.debug("Efrain:: action_print_fiscal")

        if not self.alphabot_estado:
            self.alphabot_estado = 'TO_PRINT'
