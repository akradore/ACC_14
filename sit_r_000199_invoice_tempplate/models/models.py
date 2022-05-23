# -*- coding: utf-8 -*-
from email.policy import default
from odoo.exceptions import UserError
from odoo import models, fields, _, api

import logging
_logger = logging.getLogger(__name__)


class sit_r_000199_company(models.Model):
    _inherit = 'res.company'

    sit_street2 = fields.Char('Calle Facturar', default='Vista Hermosa, Calle 4ta. y Francisco Filós')
    sit_phone = fields.Char('Teléfono Factura', default='229-0028')
    sit_fax2 = fields.Char('Fax', default='261-5996')


class sit_r_000199_invoice(models.Model):
    _inherit = 'account.move.line'
    sit_codigo = fields.Char()
    sit_name = fields.Char()
    sit_fecha_vencimiento = fields.Date()
    warehouses_id = fields.Many2one('stock.warehouse',string="Almacén")

    @api.model_create_multi
    def create(self,vals):
        for val in vals:
            if val.get('sale_line_ids'):
                get_sale_order_line = self.env['sale.order.line'].browse(val.get('sale_line_ids')[0][2])
                if get_sale_order_line:
                    val.update({'warehouses_id':get_sale_order_line.warehouses_id.id if get_sale_order_line.warehouses_id else False})
        res = super(sit_r_000199_invoice,self).create(vals)    
        return res

class sit_r_000199_invoice_line(models.Model):
    _inherit = 'account.move'
    sit_sale_order = fields.Many2one('sale.order',string="Sale Order")
    sit_fecha_vencimiento = fields.Datetime('Fecha de vencimiento', compute='get_fecha_vencimiento')
    # sit_order_line = fields.Date(related='sit_sale_order.order_line')
    sit_name = fields.Char(compute='get_custom_name')
    carrier_id=fields.Char("Método de envío", compute='get_carrier_id')

    def get_fecha_vencimiento(self):
        fecha_venc = self.env['sale.order'].search([('name','=',self.invoice_origin) ])
        _logger.info("SIT fecha_venc computada : %s, fecha_venc : %s ", fecha_venc.commitment_date , fecha_venc  )
        self.sit_fecha_vencimiento = fecha_venc.commitment_date

    def get_carrier_id(self):
        carrie_id = self.env['sale.order'].search([('name','=',self.invoice_origin) ])
        _logger.info("SIT carrier_id computada :  %s ", carrie_id.carrier_id   )
        self.carrier_id = carrie_id.carrier_id.name



    @api.model
    def get_custom_name(self):
        self.ensure_one()
        sit_name1 = self.alphabot_estado
        origen = self.invoice_origin
        try:
            sit_name1 = sit_name1.replace("]","")
            sit_name1 = sit_name1.replace("[","")
            sit_name1 = sit_name1.split("TFDM")
            sit_name = "TFDM-" + sit_name1[1] + "-" + origen
            self.sit_name = sit_name
            _logger.info("SIT sit_name : %s, sit_name1 : %s ", sit_name, sit_name1  )
        except:
            self.sit_name = self.name

    def get_cod_name(self, val):
        self.ensure_one()
        codigo_nombre = val.name
        codigo_nombre_e = codigo_nombre.find(']')
        _logger.info("SIT codigo_nombre_e : %s, codigo_nombre : %s ", codigo_nombre_e, codigo_nombre  )


        if str(codigo_nombre_e) != "-1":
            _logger.info("SIT codigo_nombre : %s, codigo_nombre : %s ", codigo_nombre, codigo_nombre  )
            B=codigo_nombre.replace("[","")
            codigo_nombre_f=B.split("] ")
            _logger.info("SIT codigo_nombre : %s, codigo_nombre_f[0] : %s ", codigo_nombre, codigo_nombre_f[0]  )
            val.sit_codigo = codigo_nombre_f[0]
            val.sit_name = codigo_nombre_f[1]
            sit_warehouse = self.env['sale.order']
            _logger.info("SIT sit_warehouse : %s", sit_warehouse )
        else:
            val.sit_codigo = ""
            val.sit_name = codigo_nombre
        return 

    def get_almac(self, val):
        self.ensure_one()
        _logger.info("SIT self : %s , val: %s", self, val  )

        sit_order = self.env['sale.order']

        _logger.info("SIT sit_order : %s ", sit_order  )
        return 

    def _get_fecha_vencimiento(self):
        fecha_venc = self.env['order.sale'].search([('name','=',self.invoice_origin) ])
        _logger.info("SIT fecha_venc computada : %s, fecha_venc : %s ", fecha_venc.commitment_date , fecha_venc  )
        return fecha_venc.commitment_date


# from odoo import models, fields, api


# class sit_r_000199_invoice_tempplate(models.Model):
#     _name = 'sit_r_000199_invoice_tempplate.sit_r_000199_invoice_tempplate'
#     _description = 'sit_r_000199_invoice_tempplate.sit_r_000199_invoice_tempplate'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
