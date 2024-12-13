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
  'depends': ['base', 'mail', 'website'],
  'data': [
    'security/ir.model.access.csv',
    # 'security/project_management_security.xml',

    # sequence
    'data/project_sprint_sequence.xml',
    'data/project_task_sequence.xml',
    'data/project_management_sequence.xml',
    'data/project_task_type_sequence.xml',
    'data/request_open_project_sequence.xml',

    # views
    'views/project_management_views.xml',
    'views/sprint_views.xml',
    'views/task_views.xml',
    'views/type_task_views.xml',
    'views/request_open_project_views.xml',
  ],
  'demo': [],
  'qweb': [],
  "license": "AGPL-3",
  'installable': True,
  'auto_install': False,
  'application': True,
}