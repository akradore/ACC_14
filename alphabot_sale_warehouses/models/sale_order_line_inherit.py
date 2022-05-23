# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    warehouses_id = fields.Many2one('stock.warehouse',string="Warehouses")
    is_warehouse = fields.Boolean()


    @api.onchange('product_id')
    def set_required_warehouse(self):
        # allow_warehouse = self.env['ir.config_parameter'].sudo().get_param('alphabot_sale_warehouses.allow_warehouse')
        # self.is_warehouse = allow_warehouse
        self.is_warehouse = True
        if self.product_id:
            if self.product_id.sale_warehouse_id:
                self.warehouses_id = self.product_id.sale_warehouse_id.id
            else:
                self.warehouses_id = self.warehouse_id

        if not self.warehouses_id:
            if self.warehouse_id:
                self.warehouses_id = self.warehouse_id

    def _prepare_procurement_values(self,group_id):
        res = super(SaleOrderLineInherit, self)._prepare_procurement_values(group_id=group_id)
        
        # res_config= self.env['res.config.settings'].sudo().search([],order="id desc", limit=1)
        # if res_config.allow_warehouse:

        # allow_warehouse = self.env['ir.config_parameter'].sudo().get_param('alphabot_sale_warehouses.allow_warehouse')
        # if allow_warehouse:
        res.update({
            'warehouse_id':self.warehouses_id,
        })

        return res

    # @api.depends(
    #     'product_id', 'customer_lead', 'product_uom_qty', 'product_uom', 'order_id.commitment_date',
    #     'move_ids', 'move_ids.forecast_expected_date', 'move_ids.forecast_availability')
    # def _compute_qty_at_date(self):

    def _compute_qty_at_date(self):

        for line in self:

            line.is_warehouse = True
            if not line.warehouses_id:
                line.warehouses_id = self.order_id.warehouse_id

            line.write({
                'warehouse_id': line.warehouses_id,
                'warehouse_id': line.warehouses_id,
                'is_warehouse': line.is_warehouse
            })

        res = super(SaleOrderLineInherit, self)._compute_qty_at_date()

        return res

    @api.onchange('warehouses_id')
    def on_change_warehouses_id(self):
        self.warehouse_id = self.warehouses_id
        dummyfloat = self.product_uom_qty
        self.product_uom_qty = 0
        self.write({
            'warehouse_id': self.warehouses_id
        })
        self.product_uom_qty = dummyfloat





