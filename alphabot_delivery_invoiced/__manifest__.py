# -*- coding: utf-8 -*-
{
    'name': 'Alphabot Delivery Invoiced',
    'summary': "Indica las ordenes facturadas",
    'description': 'Indica las ordenes facturadas',
    'category': 'Stock',
    'author': 'AlphaPos',
    'website': 'http://alphapos.biz',
    "support": "info@alphapos.biz",
    "license": "Other proprietary",
    'version': '0.1.22.4.27',      
    'depends': ['base','alphabot_invoicing','sale','sale_stock', 'alphabot_sale_warehouses'],
    'data': [
        'data/automatic_picking_data.xml',
        'security/ir.model.access.csv',
        'views/stock_picking.xml',
        'views/sale_order.xml'
    ],
    'qweb': [
    ],
    'installable': True,
    'application': False,
    #'image': ['static/description/alpha_logo.png'],
}
