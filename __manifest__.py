# -*- coding: utf-8 -*-
{
    'name': 'Pre‑Printed Forms Writer',
    'version': '1.0',
    'summary': 'Manage pre‑printed forms with overlay items',
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
