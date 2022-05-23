# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    monto_alerta = fields.Float(string='Alerta de monto',
                                help="El mensaje de alerta  va a aparecer cuando se supere el límite. "
                                     "Se deben realizar los pagos para colocar la cuenta en cero",
                                default=0.00)
    monto_bloqueo = fields.Float(string='Bloqueo por monto',
                                 help="No se pueden hacer ventas al cliente cuando se supere su límite de crédito. "
                                      "Se deben realizar los pagos para colocar la cuenta en cero",
                                 default=0.00)
    monto_adeudado = fields.Float(string="Total de Venta", compute="compute_due_amount", store=False)
    limite_activo = fields.Boolean("Límite de credito", default=False)
    has_due = fields.Boolean(compute="check_due", store=False)
    is_warning = fields.Boolean(compute="check_due", store=False)

    def check_due(self):
        """To show the due amount and warning stage"""
        self.has_due = False
        if self.limite_activo:
            if self.monto_adeudado > 0:
                self.has_due = True

        self.is_warning = False
        if self.limite_activo:
            if self.monto_adeudado >= self.monto_alerta:
                self.is_warning = True

    def compute_due_amount(self):
        for rec in self:
            if not rec.id:
                continue
            rec.monto_adeudado = rec.credit - rec.debit

    @api.constrains('monto_alerta', 'monto_bloqueo')
    def constrains_warning_stage(self):
        if self.limite_activo:
            if self.monto_alerta >= self.monto_bloqueo:
                #if self.monto_bloqueo > 0:
                raise UserError(_(
                    "El monto de Alarma debe ser menor al monto de Bloqueo"))

    def check_credit_sale(self, venta):
        if self.limite_activo:
            if self.monto_adeudado >= self.monto_bloqueo:
                raise UserError(_(
                    "%s está bloqueado con cuentas por pagar de %s%s") % (
                    self.name, self.currency_id.symbol, round(self.monto_adeudado, 2)))
            if (self.monto_adeudado + venta) >= self.monto_bloqueo:
                raise UserError(_(
                    "Esta venta supera el límite del crédito de %s de %s%s") % (
                    self.name, self.currency_id.symbol, round(self.monto_bloqueo, 2)))
        else:
            raise UserError(_(
                "%s no tiene activo un límite de crédito") % (self.name))


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    has_due = fields.Boolean(related='partner_id.has_due')
    is_warning = fields.Boolean(related='partner_id.is_warning')
    monto_bloqueo = fields.Float(related='partner_id.monto_bloqueo')
    monto_adeudado = fields.Float(related='partner_id.monto_adeudado')


    def check_sale_type(self):
        venta_credito = False
        for line in self.payment_term_id.line_ids:
            if line.days != 0:
                venta_credito = True
        return venta_credito

    def _action_confirm(self):
        """To check the selected customers due amount is exceed than
        blocking stage"""
        if self.check_sale_type():
            self.partner_id.check_credit_sale(self.amount_total)
        return super(SaleOrder, self)._action_confirm()


    def _create_invoices(self, grouped=False, final=False, date=None):
        respuesta = super(SaleOrder, self)._create_invoices(grouped, final, date)
        for sale in respuesta:
            if sale.check_sale_type():
                sale.partner_id.check_credit_sale(self.amount_total)
        return respuesta


class AccountMove(models.Model):
    _inherit = 'account.move'

    has_due = fields.Boolean(related='partner_id.has_due')
    is_warning = fields.Boolean(related='partner_id.is_warning')
    monto_bloqueo = fields.Float(related='partner_id.monto_bloqueo')
    monto_adeudado = fields.Float(related='partner_id.monto_adeudado')

    def check_sale_type(self):
        venta_credito = False
        for line in self.invoice_payment_term_id.line_ids:
            if line.days != 0:
                venta_credito = True
        return venta_credito

    def action_post(self):
        """To check the selected customers due amount is exceed than
        blocking stage"""
        pay_type = ['out_invoice', 'out_refund', 'out_receipt']
        for rec in self:
            if rec.move_type in pay_type:
                if rec.check_sale_type():
                    rec.partner_id.check_credit_sale(self.amount_total)
        return super(AccountMove, self).action_post()

            
