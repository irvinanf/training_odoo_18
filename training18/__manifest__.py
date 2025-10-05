# -*- coding: utf-8 -*-
{
    'name': "TRAINING18",

    'summary': "Training Odoo 18",

    'description': """
Modul untuk latihan technical Odoo 18
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        #security
        'views/purchase_order_view.xml',
        'views/master_product_view.xml',
        'views/menus.xml',
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        #views
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

