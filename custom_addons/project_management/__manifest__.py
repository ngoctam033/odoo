# -*- coding: utf-8 -*-
{
  'name': 'Project Management',
  'version': '1.0.0.0.0',
  'category': 'Test',
  'author': 'Nguyen Ngoc Tam',
  'website': "https://bap.bemo-cloud.com/",
  'company': 'BAP Solutions',
  'maintainer': 'BAP Solutions',
  'summary': 'Test',
  "description": """Try to test""",
  'depends': ['base', 'mail'],
  'data': [
    # security
    'security/project_management_category.xml',
    'security/project_management_groups.xml',
    'security/project_management_rules.xml',
    'security/ir.model.access.csv',

    # sequence
    'data/project_sprint_sequence.xml',
    'data/project_task_sequence.xml',
    'data/project_management_sequence.xml',
    'data/project_task_type_sequence.xml',
    'data/request_open_project_sequence.xml',
    'data/request_close_project_sequence.xml',

    # mail server action
    'data/mail_server.xml',

    # mail template
    'data/mail_templates.xml',

    # assets
    'views/assets.xml',

    # views
    'views/sprint_views.xml',
    'views/task_views.xml',
    'views/type_task_views.xml',
    'views/cancel_reason_wizard_views.xml',
    'views/request_open_project_views.xml',
    'views/request_close_project_views.xml',
    'views/project_management_views.xml',
  ],
  'demo': [],
  'qweb': [
      'static/src/xml/templates_button.xml',
  ],
  'post_init_hook': 'generate_demo_data',
  "license": "AGPL-3",
  'installable': True,
  'auto_install': False,
  'application': True,
}