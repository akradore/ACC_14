# -*- coding: utf-8 -*-
{
    'name': 'Alphabot Credit Limit',
    'summary': "Limite de crédito para los clientes",
    'description': 'Limite de crédito para los clientes',
    'category': 'Accounting/Accounting',
    'author': 'AlphaPos',
    'website': 'http://alphapos.biz',
    "support": "info@alphapos.biz",
    "license": "Other proprietary",
    'sequence': 10,
    'version': '0.1.22.4.7',
    'depends': ['base', 'account', 'sale'],
    'data': [
        "security/credit_limit_data.xml",
        'views/credit_limit_view.xml',
    ],
    'qweb': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
