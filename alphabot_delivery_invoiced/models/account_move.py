from odoo import models, fields, _, api


class AccountMove(models.Model):
    _inherit = "account.move"

    # alphabot_estado = fields.Char(string="Estado imp. fiscal", size=1024, copy=False)
    # alphabot_cliente_name = fields.Char(string="Cliente imp. fiscal", size=1024)
    # alphabot_cliente_ruc = fields.Char(string="RUC imp. fiscal", size=1024)
    # alphabot_devol_fact = fields.Char(string="Factura en Devol.", size=1024)
    #
    # alphabot_fiscal_data = fields.Boolean(compute='_compute_alphabot_settings', string='Campos para imp. fiscal ...')
    # alphabot_manual_printing = fields.Boolean(compute='_compute_alphabot_settings', string='Botón impresión fiscal')

    invoice_date_first = fields.Date(related='invoice_date', string='Fecha', readonly=False, copy=False)

    alphabot_estado_short_display = fields.Char(compute='_compute_fiscal_id_data_short', string='ID Fiscal')

    def _compute_fiscal_id_data_short(self):
        for rec in self:
            saux = ""
            if type(rec.alphabot_estado) == (str):
                if len(rec.alphabot_estado) > 23:
                    saux = rec.alphabot_estado[-9:][0:8]
            rec.alphabot_estado_short_display = saux


    # usado en delivery invoice y en otras
    def _is_move_invoiced(self):
        # ahora solo se confirma que la factura este posted
        # for rec in self:
        #     if rec.state == 'cancel':
        #         continue
        #     if rec.state == 'posted':
        #         return True
        # return False
        for rec in self:
            if rec.state == 'cancel':
                continue
            if rec.alphabot_estado:
                if rec.alphabot_estado.find('FIS-ID') >= 0:
                    return True
        return False
        
