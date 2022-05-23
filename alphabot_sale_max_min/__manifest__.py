# -*- coding: utf-8 -*-
{
    'name': 'Alphabot Sale Max-Min',  
    'summary': "Precio mínimo y máximo en Ventas",
    'description': 'Precio mínimo y máximo en Ventas',
    'category': 'Sale',
    'author': 'AlphaPos',
    'website': 'http://alphapos.biz',
    "support": "info@alphapos.biz",
    "license": "Other proprietary",
    'version': '0.1.22.3.28',      
    'depends': ['base','sale'],
    'data': [
        'data/sale_order_price_group.xml',
        'security/price_security.xml',
        'views/sale_order_min_max_price.xml'
    ],
    'qweb': [
    ],
    'installable': True,
    'application': False,
    #'image': ['static/description/alpha_logo.png'],
}
