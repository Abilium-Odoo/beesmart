# -*- coding: utf-8 -*-
{
    'name': "BeeSmart Core Module",

    'summary': """Provides basic beesmart customizations""",

    'description': """
       Adds ubuntu font to report
    """,

    'author': "Abilium GmbH",
    'website': "https://www.abilium.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': '',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'web',
        'helpdesk_mgmt',
        'contacts'
    ],

    # always loaded
    'data': [
        'views/login.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'qweb': [
        'static/src/xml/*.xml'
    ],

}