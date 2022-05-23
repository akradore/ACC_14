from odoo.exceptions import UserError
from odoo import models, fields, _, api
from odoo.tests import Form
# from odoo.tools.float_utils import float_compare, float_is_zero, float_round
import threading
import time
import logging

_logger = logging.getLogger(__name__)

class PickingTypeInherit(models.Model):
    _inherit = "stock.picking.type"

    def _compute_picking_count(self):
        super(PickingTypeInherit, self)._compute_picking_count()
        for record in self:
            if record.code == 'outgoing':
                record['count_picking_ready'] = self.env['stock.picking'].search_count(
                    [('state', '=', 'done'), ('invoice_state_display', '=', 'invoiced'),
                     ('picking_delivery_state', '=', 'todelivery'), ('picking_type_id', '=', record.id)])

    def get_action_picking_tree_ready(self):
        if self[0].code == 'outgoing':
            return self._get_action('alphabot_delivery_invoiced.action_picking_tree_todelivery')
        return super(PickingTypeInherit, self).get_action_picking_tree_ready()


class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    invoice_qty = fields.Float(compute='_compute_invoice_qty', store=False, readonly=True)

    invoice_state_display = fields.Selection(selection=[
        ('invoiced', 'Facturado'),
        ('invoiced_partial', 'Parcialmente facturado'),
        ('draft', 'No facturado'),
    ], string='Facturación', default='draft', store=True, copy=False)

    invoice_state = fields.Selection(selection=[
        ('invoiced', 'Facturado'),
        ('invoiced_partial', 'Parcialmente facturado'),
        ('draft', 'No facturado'),
    ], string='Facturación', default='draft', compute='_compute_invoice_state')

    picking_type_code_domain = fields.Boolean(compute='_compute_picking_type_code_domain')

    invoice_move_ids = fields.One2many('account.move',
                                       compute='_compute_invoice_move_ids', groups='base.group_user', readonly=False,
                                       store=False)

    invoice_date_first = fields.Date(
        string='Fecha Factura',
        copy=False,
        store=True
        # default=fields.Date.context_today
    )

    invoice_alphabot_estado = fields.Char(string="ID Fiscal", size=1024, copy=False)

    picking_delivery_state = fields.Selection(selection=[
        ('delivered', 'Entregado'),
        ('todelivery', 'Para despachar'),
        ('draft', 'Incompleto'),
    ], default='draft', copy=False, string='Entrega')

    picking_auntovalidate_timeout = fields.Integer(default=0)

    def do_state_delivered(self):
        for rec in self:
            if rec.picking_delivery_state == 'todelivery':
                rec.action_picking_delivery_state()

    def action_picking_delivery_state(self):
        orginal_state = new_state = self.picking_delivery_state
        if orginal_state == 'todelivery':
            new_state = 'delivered'
            message = _('Para despachar -> Entregado')
        elif orginal_state == 'delivered':
            new_state = 'todelivery'
            message = _('Entregado -> Para despachar')
        if orginal_state != new_state:
            self.picking_delivery_state = new_state
            self.message_post(body=_(message),
                              message_type='comment',
                              subtype_xmlid='mail.mt_note')

    def _compute_invoice_move_ids(self):
        for rec in self:
            rec.invoice_move_ids = rec.sale_id.invoice_ids

    def _compute_picking_type_code_domain(self):
        for rec in self:
            if rec.picking_type_code == 'outgoing':
                rec.picking_type_code_domain = True
            else:
                rec.picking_type_code_domain = False

    # @api.depends('sale_line_id')
    def _compute_invoice_qty(self):
        for rec in self:
            # total_qty = 0
            # done = True
            # for line in rec.move_line_ids:
            #     total_qty += line.move_id.invoice_items_qty
            #     if line.move_id.state not in ('cancel', 'done'):
            #         done = False
            # rec.invoice_qty = total_qty
            #
            if rec.picking_type_code == 'outgoing':
                moves = rec.mapped('move_lines').filtered(lambda move: move.state not in ('cancel', 'done'))
                rec.invoice_qty = len(moves)
                if len(moves) == 0:
                    if rec.picking_delivery_state == 'draft':
                        rec.picking_delivery_state = 'todelivery'
            else:
                rec.invoice_qty

    def _compute_invoice_state(self):
        for rec in self:
            if rec.picking_type_code_domain:
                if rec.state == 'cancel':
                    # si el pedido se canceló ajusto el estado
                    if 'draft' != rec.invoice_state_display:
                        rec.invoice_state_display = 'draft'
                    if 'draft' != rec.picking_delivery_state:
                        rec.picking_delivery_state = 'draft'
                    rec.invoice_state = 'draft'

                else:
                    states = []
                    for line in rec.move_ids_without_package:
                        move_state = self.env['stock.move'].browse(line.id).invoice_item_state
                        states.append(move_state)

                    draft_exist = 'draft' in states
                    invoiced_exist = 'invoiced' in states

                    new_state = 'draft'
                    if invoiced_exist and draft_exist:
                        new_state = 'invoiced_partial'
                    elif not invoiced_exist:
                        new_state = 'draft'
                    else:
                        new_state = 'invoiced'
                    rec.invoice_state = new_state

                    # si hay un cambio en el estado del pago
                    # proceso esa orden
                    if new_state != rec.invoice_state_display:
                        rec.invoice_state_display = new_state

                    if rec.sale_id.invoice_ids:
                        inv = rec.sale_id.invoice_ids[0]
                        # ojo, uno picking puede tener mas de un factura, aqui solo mostramos la primera
                        if inv._is_move_invoiced():
                            if inv.invoice_date_first != rec.invoice_date_first:
                                rec.invoice_date_first = inv.invoice_date_first
                            id_fiscal = inv.alphabot_estado
                            if id_fiscal:
                                if len(id_fiscal) >= 41:
                                    id_fiscal = id_fiscal[19: 41]
                                    if id_fiscal != rec.invoice_alphabot_estado:
                                        rec.invoice_alphabot_estado = id_fiscal

            else:
                rec.invoice_state = 'draft'
        return True

    def is_all_good_ready(self):
        for rec in self:
            for line in rec.move_ids_without_package:
                move = self.env['stock.move'].browse(line.id)
                if move.product_type == 'product':
                    if move.product_uom_qty > move.reserved_availability:
                        _produ = move.product_tmpl_id
                        _ubicacion = move.location_id
                        free = _produ.with_context(location=_ubicacion.id)._product_available(False, False).get(
                            _produ.id).get(
                            'free_qty')
                        if move.product_uom_qty > free:
                            return False
        return True

    def picking_move_no_decimals_validate(self):
        for rec in self:
            if rec.state != 'cancel':
                for move in rec.move_lines:
                    # verifico que la cantidad siempre sea entera (just in case)
                    # el error se puede producir por un Kit mal definido, que origne una cantidad de producto con decimales
                    qty_decimal = int((move.product_qty - int(move.product_qty))*1000)
                    if (qty_decimal != 0):
                        raise UserError(_("Verifique las cantidades de los productos en las transferencias de almacén. "
                                          "Valores con decimales no son permitidos. "
                                          "Es posible que un producto tipo KIT no esté bien definido."))

    def button_validate(self):
        for rec in self:
            if rec.picking_type_code_domain:
                rec.picking_move_no_decimals_validate()
                if rec.picking_delivery_state == 'draft':
                    if not rec.is_all_good_ready():
                        raise UserError(_(
                            "La orden tiene productos que no están disponibles. Por favor revise el contenido de la orden."))

                if rec.invoice_state_display != 'invoiced':
                    if self.user_has_groups('stock.group_stock_manager'):
                        message = _('IMPORTANTE: Pedido validado sin estado de facturación')
                        rec.message_post(body=_(message),
                                         message_type='comment',
                                         subtype_xmlid='mail.mt_note')
                        rec.picking_delivery_state = 'todelivery'
                    else:
                        raise UserError(_(
                            "La orden de entrega debe estar en estado 'Facturado'"))
        return super(StockPickingInherit, self).button_validate()

    def _pre_action_done_hook(self):
        resp = super(StockPickingInherit, self)._pre_action_done_hook()

        if resp == True:
            return True

        if resp['res_model'] == 'stock.backorder.confirmation':
            resp = Form(self.env['stock.backorder.confirmation'].with_context(resp['context'])).save().process()
        else:
            resp = Form(self.env['stock.immediate.transfer'].with_context(resp['context'])).save().process()

        return resp

    @api.model
    def _upddate_pickings(self, domain_filter):
        picking_obj = self.env["stock.picking"]
        pickings = picking_obj.search(domain_filter, order='write_date desc', limit=500)
        _logger.info(len(pickings))
        pickings._compute_invoice_qty()
        pickings._compute_invoice_state()
        # for picking in pickings:
        #     # _logger.info("_upddating %s", picking)
        #     picking._compute_invoice_qty()
        #     picking._compute_invoice_state()

    @api.model
    def _validate_pickings(self, domain_filter):
        picking_obj = self.env["stock.picking"]
        pickings = picking_obj.search(domain_filter, order='write_date desc', limit=500)
        _logger.info(len(pickings))
        IDs = []
        for picking in pickings:
            if picking.picking_type_code_domain:
                # esto es para hacer la autovalidación
                # si esta en el dominio 'outgoing'
                # tiene factura
                # y all listo
                # picking.picking_auntovalidate_timeout = picking.picking_auntovalidate_timeout + 1
                is_invoice = True
                for inv in picking.sale_id.invoice_ids:
                    if not inv._is_move_invoiced():
                        is_invoice = False
                if is_invoice and \
                        picking.invoice_state_display == 'invoiced' and \
                        picking.is_all_good_ready():
                    IDs.append(picking.id)

        if len(IDs) > 0:
            if len(IDs) > 5:
                IDs = IDs[:5]  # maximo proceso 1 documentos
            for idx in IDs:
                _pick = self.env["stock.picking"].browse(idx)
                _logger.info(_pick.name)
                _pick.button_validate()
                # with api.Environment.manage():
                #     new_cr = self.pool.cursor()
                #     _self = self.with_env(self.env(cr=new_cr))
                #     _self.env["stock.picking"].browse(idx).button_validate()
                #     new_cr.commit()
                #     new_cr.close()

        return True

    @api.model
    def _run_auto(self):
        self._upddate_pickings([("state", "!=", "cancel"),("state", "!=", "done"),("state", "!=", "draft"),("picking_type_code", "=", "outgoing"),
                                ("invoice_state_display", "!=", "invoiced"), ("invoice_state_display", "!=", "cancel")])
        self._validate_pickings([("state", "=", "assigned"), ("invoice_state_display", "=", "invoiced"), ("picking_type_code", "=", "outgoing")])
        return True
