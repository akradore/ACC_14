# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError, UserError, Warning


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    pro_min_sale_price = fields.Float(string="Precio mínimo")
    pro_max_sale_price = fields.Float(string="Precio máximo")
    is_allow_to_set_price = fields.Boolean(compute = "compute_is_allow_to_set_price")

    def compute_is_allow_to_set_price(self):
        for rec in self:
            rec.is_allow_to_set_price = False
            if self.env.user.has_group('alphabot_sale_max_min.group_set_price_in_product'):
                rec.is_allow_to_set_price = True
                
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    pro_min_sale_price = fields.Float(
        related="product_id.pro_min_sale_price", string="Precio mínimo", readonly=True)
    pro_max_sale_price = fields.Float(
        related="product_id.pro_max_sale_price", string="Precio máximo", readonly=True)

    @api.onchange('product_id')
    def product_id_change(self):
        if self.product_id:
            res = super(SaleOrderLine, self).product_id_change()
            self.pro_min_sale_price = self.product_id.pro_min_sale_price
            self.pro_max_sale_price = self.product_id.pro_max_sale_price

            return res

    @api.onchange('price_unit')
    def product_price_change(self):
        if self.price_unit:
            if (self.pro_min_sale_price > 0 and self.price_unit < self.pro_min_sale_price):
                warning_mess = {
                    'message': ('El precio debe ser superior a: %0.2f' % self.pro_min_sale_price),
                    'title': "Warning"
                }
                return {'warning': warning_mess}
            if (self.pro_max_sale_price > 0 and self.price_unit > self.pro_max_sale_price):
                warning_mess = {
                    'message': ('El precio debe ser inferior a: %0.2f' % self.pro_max_sale_price),
                    'title': "Warning"
                }
                return {'warning': warning_mess}

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _action_confirm(self):

        res = super(SaleOrder, self)._action_confirm()

        if self and self.order_line:
            for rec in self.order_line:
                if rec.price_unit:
                    if (rec.pro_min_sale_price > 0 and rec.price_unit < rec.pro_min_sale_price) or (rec.pro_max_sale_price > 0 and rec.price_unit > rec.pro_max_sale_price):
                        allow_price = self.env.user.has_group(
                            'alphabot_sale_max_min.group_sale_order_product_price')
                        if not allow_price:
                            raise UserError(("Un precio está fuera de los límites permitidos."))

        return res
                