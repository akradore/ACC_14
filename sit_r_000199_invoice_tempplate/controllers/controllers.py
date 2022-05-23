# -*- coding: utf-8 -*-
# from odoo import http


# class SitR000199InvoiceTempplate(http.Controller):
#     @http.route('/sit_r_000199_invoice_tempplate/sit_r_000199_invoice_tempplate/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sit_r_000199_invoice_tempplate/sit_r_000199_invoice_tempplate/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sit_r_000199_invoice_tempplate.listing', {
#             'root': '/sit_r_000199_invoice_tempplate/sit_r_000199_invoice_tempplate',
#             'objects': http.request.env['sit_r_000199_invoice_tempplate.sit_r_000199_invoice_tempplate'].search([]),
#         })

#     @http.route('/sit_r_000199_invoice_tempplate/sit_r_000199_invoice_tempplate/objects/<model("sit_r_000199_invoice_tempplate.sit_r_000199_invoice_tempplate"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sit_r_000199_invoice_tempplate.object', {
#             'object': obj
#         })
