# -*- coding: utf-8 -*-

from odoo import fields, models,api

class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    sale_warehouse_id = fields.Many2one('stock.warehouse',string="Sale Warehouse")
