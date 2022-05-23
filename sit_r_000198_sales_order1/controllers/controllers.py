# -*- coding: utf-8 -*-
# from odoo import http


# class SitR000198SalesOrder1(http.Controller):
#     @http.route('/sit_r_000198_sales_order1/sit_r_000198_sales_order1/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sit_r_000198_sales_order1/sit_r_000198_sales_order1/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sit_r_000198_sales_order1.listing', {
#             'root': '/sit_r_000198_sales_order1/sit_r_000198_sales_order1',
#             'objects': http.request.env['sit_r_000198_sales_order1.sit_r_000198_sales_order1'].search([]),
#         })

#     @http.route('/sit_r_000198_sales_order1/sit_r_000198_sales_order1/objects/<model("sit_r_000198_sales_order1.sit_r_000198_sales_order1"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sit_r_000198_sales_order1.object', {
#             'object': obj
#         })
