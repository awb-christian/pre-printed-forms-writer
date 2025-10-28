{
    'name': 'Pre-Printed Forms Writer',
    'summary': 'Manage pre-printed forms with overlay items',
    'version': '1.0',
    'category': 'Tools',
    'author': 'Your Name',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/pre_printed_form_views.xml',
        'views/overlay_text_item_views.xml',
        'views/overlay_config_item_views.xml',
        'views/ir_attachment_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
