# -*- coding: utf-8 -*-
{
    'name': "contract_management_system",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'board'],

    # always loaded
    'data': [
        'data/cron.xml',
        'data/email_template.xml',
        'data/system_parameter.xml',
        'security/security.xml',
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'views/views_contract.xml',
        # 'views/views_contractFiles.xml',
        'views/views_contractLine.xml',
        'views/views_contractTermin.xml',
        'views/templates.xml',
        'views/menuitem_views.xml',
        'views/views_contractDashboard.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'license': 'LGPL-3',
    'application': True,
}
