{
    'name': 'Demo Widget',
    'version': '1.0',
    'category': 'Custom',
    'summary': 'Module to add custom widget',
    'description': 'This module adds a custom widget.',
    'author': 'Tamnn',
    'depends': ['base', 'web', 'website', 'web_editor'],
    'data': [
        'security/ir.model.access.csv',

        'views/my_model_views.xml',
        'views/feedback_views.xml',

        'views/templates.xml',

        # 'views/feedback_snippet_option.xml',    
        'views/feedback_form_snippet.xml',

        'demo/demo_data.xml',
    ],
    'qweb': [
        "static/src/xml/clickme_button.xml",
        "static/src/xml/templates_lesson4.xml",
    ],

    'installable': True,
    'application': True,
}