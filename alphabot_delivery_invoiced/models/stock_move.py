from odoo.exceptions import UserError
from odoo import models, fields, _, api

import logging
_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    invoice_items_qty = fields.Float(compute='_compute_invoice_items_qty', store=False, readonly=True)
    invoice_items_price = fields.Float(compute='_compute_invoice_items_qty', store=False, readonly=True)
    invoice_items_subtotal = fields.Float(compute='_compute_invoice_items_qty', store=False, readonly=True)

    invoice_item_state = fields.Selection(selection=[
            ('invoiced', 'Facturado'),
            ('draft', 'No facturado'),
        ], string='Facturación', compute='_compute_invoice_item_state')

    picking_item_type_code_domain = fields.Boolean(compute='_compute_picking_item_type_code_domain')

    def _compute_picking_item_type_code_domain(self):
        for rec in self:
            if rec.picking_id.picking_type_code == 'outgoing':
                rec.picking_item_type_code_domain = True
            else:
                rec.picking_item_type_code_domain = False

    # esto se trae las catidades facturadas de cada linea del pedido de venta
    # y lo almacena en una variable local de este modelo
    @api.depends('product_uom_qty')
    def _compute_invoice_items_qty(self):
        for rec in self:
            rec.invoice_items_qty = rec.sale_line_id.qty_invoiced
            if not rec.bom_line_id:
                rec.invoice_items_price = rec.sale_line_id.price_unit
                rec.invoice_items_subtotal = rec.sale_line_id.price_subtotal
            else:
                bom_id = rec.bom_line_id.bom_id
                combo_qty= bom_id.product_qty
                produ_qty  = 1
                for bom_lines in bom_id.bom_line_ids:
                    if bom_lines.product_id.id == rec.product_id.id:
                        produ_qty = bom_lines.product_qty
                produc_fact =   produ_qty/combo_qty
                rec.invoice_items_price = rec.sale_line_id.price_unit * produc_fact
                rec.invoice_items_subtotal = rec.sale_line_id.price_subtotal * produc_fact

    # esto define si una linea esta facturada o no
    # con el criterio de que la cantidad vendidad - lo facturado = 0
    @api.depends('product_uom_qty', 'sale_line_id')
    def _compute_invoice_item_state(self):
        for rec in self:
            qty = rec.product_uom_qty
            if rec.bom_line_id:
                qty = (rec.bom_line_id.bom_id.product_qty / rec.bom_line_id.product_qty) * qty
            n_fact = rec.sale_line_id.qty_invoiced * rec.sale_line_id.product_uom.factor_inv
            pendiente = qty - n_fact
            rec.invoice_item_state = 'draft'
            if pendiente <= 0:
                origin_invoice = rec.sale_line_id.invoice_lines.move_id
                # esto es para ver que el documento tenga la factura fiscal impresa
                if origin_invoice._is_move_invoiced():
                    rec.invoice_item_state = 'invoiced'


