# -*- coding: utf-8 -*-
{
    'name': 'Alphabot Sale Warehouses',
    'summary': "Uso de almacenes en Ventas",
    'description': 'Uso de almacenes en Ventas',
    'category': 'Sale',
    'author': 'AlphaPos',
    'website': 'http://alphapos.biz',
    "support": "info@alphapos.biz",
    "license": "Other proprietary",
    'version': '0.1.22.3.29',
    'depends': ['base','sale','stock','sale_management'],
    'data': [
        "security/security.xml",
        "views/views.xml",
        "security/ir.model.access.csv",
        "views/product_template_view.xml",
        "views/product_product_view.xml",
        "views/sale_order.xml",
        'views/sale_order_views.xml',
        "views/res_config_settings.xml",
        'views/product_template_inherit.xml',
        'views/product_product_inherit.xml',
    ],
    'qweb': [
        "static/src/xml/locations_hierarchy.xml"
    ],
    'installable': True,
    'application': False,
    #'image': ['static/description/alpha_logo.png'],
}
