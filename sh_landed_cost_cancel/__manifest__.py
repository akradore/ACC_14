# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

{
    "name": "Cancel Landed Cost",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Warehouse",
    "license": "OPL-1",
    "summary": "Landed Cost Cancel, Reset and Cancel Landed Cost, Mass multiple landed costs, Multiple landed costs Cancel, Cancel Land Cost, Cancel Cost, Cancel and delete LAnded Cost, Delete Landed Cost Odoo",
    "description": """This module helps to cancel landed costs. You can also cancel multiple landed costs from the tree view. You can cancel the landed costs in 3 ways,

1) Cancel Only: When you cancel the landed cost then the landed cost is canceled and the state is changed to "cancelled".
2) Cancel and Reset to Draft: When you cancel landed costs, first landed costs is canceled and then reset to the draft state.
3) Cancel and Delete: When you cancel the landed costs then first landed cost is canceled and then landed cost will be deleted.""",
    "version": "14.0.1",
    "depends": [
                "stock_landed_costs",

    ],
    "application": True,
    "data": [
        'security/stock_security.xml',
        'data/data.xml',
        'views/stock_config_settings.xml',
        'views/views.xml',
    ],
    "images": ["static/description/background.png", ],
    "auto_install": False,
    "installable": True,
    "price": 20,
    "currency": "EUR"
}