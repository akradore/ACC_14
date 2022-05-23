from odoo.exceptions import UserError
from odoo import models, fields, _, api
from odoo.tests import Form
# from odoo.tools.float_utils import float_compare, float_is_zero, float_round
import threading
import time


class SalesOrderInherit(models.Model):
    _inherit = "sale.order"

    def lines_picks_asign(self):
        for rec in self:
            for picks in rec.picking_ids:
                if picks.state != 'cancel':
                    picks.picking_move_no_decimals_validate()
                    for move in picks.move_lines:
                        move._action_assign()
        self.env.cr.commit()

    def lines_chechk_free_quantity(self):
        for rec in self:
            for picks in rec.picking_ids:
                if picks.state != 'cancel':
                    for move in picks.move_lines:
                        move._action_assign()
                    if not picks.is_all_good_ready():
                        return False
            for lines in rec.order_line:
                if lines.product_type == 'product':
                    _produ = lines.product_template_id
                    _ubicacion = lines.warehouses_id.lot_stock_id
                    dummy = _ubicacion.display_name
                    if lines.qty_to_deliver > lines.qty_available_today:
                        # dif = lines.qty_to_deliver - lines.qty_available_today
                        # free = _produ.with_context(location=_ubicacion.id)._product_available(False, False).get(_produ.id).get('free_qty')
                        # if dif > free:
                        #     return False
                        return False
        return True

    # def action_confirm(self):
    #     # for rec in self:
    #     #     if not rec.lines_chechk_free_quantity():
    #     #         raise UserError(_("Hay productos que no están disponibles. Verifique la orden"))
    #     return super(SalesOrderInherit, self).action_confirm()

    def _create_invoices(self, grouped=False, final=False, date=None):
        for rec in self:
            rec.lines_picks_asign()
            #debo verificar la orden, y tambien los picking
            if not rec.lines_chechk_free_quantity():
                raise UserError(_("Hay productos que no están disponibles. Verifique la orden"))
        return super(SalesOrderInherit, self)._create_invoices(grouped, final, date)

    def write(self, vals):
        #if not self.user_has_groups('sales_team.group_sale_manager'):
        for rec in self:
            is_not_cancel = True
            if 'state' in vals:
                if vals['state'] == 'cancel':
                    is_not_cancel = False
            if is_not_cancel:
                if rec.invoice_ids:
                    for inv in rec.invoice_ids:
                        if not (inv.state == 'draft' or inv.state == 'cancel'):
                            if self.user_has_groups('sales_team.group_sale_manager'):
                                message = _("IMPORTANTE: Ha autorizado modificar un pedido de venta con factura")
                                rec.message_post(body=_(message),
                                                 message_type='comment',
                                                 subtype_xmlid='mail.mt_note')
                            else:
                                raise UserError(_("No puede modificar un pedido de venta con factura. "
                                                  "Pueden intentar cancelar y luego convertir a presupuesto."))
                if rec.picking_ids:
                    for pick in rec.picking_ids:
                        if (pick.state == 'done'):
                            if self.user_has_groups('sales_team.group_sale_manager'):
                                message = _("IMPORTANTE: Ha autorizado modificar un pedido de venta con ordenes de despacho")
                                rec.message_post(body=_(message),
                                                 message_type='comment',
                                                 subtype_xmlid='mail.mt_note')
                            else:
                                raise UserError(_("No puede modificar un pedido de venta con ordenes de despacho. "
                                                  "Pueden intentar cancelar y luego convertir a presupuesto."))
        return super().write(vals)
