# -*- coding: utf-8 -*-

from email.policy import default
import re
from this import d
from unicodedata import name
from unittest import result
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _
from dateutil.relativedelta import relativedelta 
import logging
_logger = logging.getLogger(__name__)


class sit_albaran(models.Model):
#     _name = 'sit_albaran.sit_albaran'
     _inherit = 'stock.picking'
     _description = 'sit_albaran.sit_albaran'
     # R-000198
     sit_forma_de_pago = fields.Char('Forma de pago', related='sale_id.payment_term_id.name' , tracking=True )
     sit_vendedor = fields.Char('Vendedor', related='sale_id.user_id.name' , tracking=True )
     sit_telefono_cliente = fields.Char('Telefono', related='partner_id.phone' , tracking=True )
     sit_mobile_cliente = fields.Char('Mobil', related='partner_id.mobile' , tracking=True )
     sit_ref = fields.Char('Referencia', related='invoice_move_ids.ref' , tracking=True )


class SIT_StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    price_unit = fields.Float()
    price_subtotal = fields.Float()

class SIT_StockMove(models.Model):
    _inherit = 'stock.move'

    price_subtotal = fields.Float()

