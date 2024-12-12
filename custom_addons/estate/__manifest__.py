# -*- coding: utf-8 -*-
{
  'name': 'Real Estate',
  'version': '1.0.0.0.0',
  'category': 'Test',
  'author': 'Nguyen Ngoc Tam',
  'website': "https://bap.bemo-cloud.com/",
  'company': 'BAP Solutions',
  'maintainer': 'BAP Solutions',
  'summary': 'Test',
  "description": """Try to test""",
  'depends': ['base', 'mail', 'website'],
  'data': [
    'security/res_groups.xml',
    'security/ir.model.access.csv',
    
    'views/estate_offer_views.xml',
    'views/estate_tag_views.xml',
    'views/estate_type_views.xml',
    'views/estate_views.xml',
    'views/estate_report_views.xml',

    'views/estate_menu_views.xml',
    
    'views/res_users_views.xml',

    # views templates
    'views/property_list_template.xml',

    'demo/demo_estate_property_type.xml',
    'demo/demo_res_partner.xml',
    'demo/demo_estate_property.xml',
    'demo/demo_estate_tag.xml',
    'demo/demo_estate_property_offer.xml',
  ],
  'demo': [],
  'qweb': [],
  "license": "AGPL-3",
  'installable': True,
  'auto_install': False,
  'application': True,
}