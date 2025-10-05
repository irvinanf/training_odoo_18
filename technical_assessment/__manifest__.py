# -*- coding: utf-8 -*-
{
    'name': "technical_assessment",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Module pemesanan ruangan meeting for technical assessment
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
        'views/master_ruangan_views.xml',
        'views/pemesanan_ruangan_views.xml',
        'views/menuitem_views.xml',
        'security/res_groups.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

