# -*- coding: utf-8 -*-
from odoo import models, fields

class OverlayConfigurationItem(models.Model):
    _name = 'overlay.config.item'
    _description = 'Overlay Configuration Item'

    name = fields.Char(string='Config Name', required=True)
    form_id = fields.Many2one(
        comodel_name='pre.printed.form',
        string='Pre‑Printed Form',
        ondelete='cascade'
    )
    config_value = fields.Char(string='Value')
    sequence = fields.Integer(string='Sequence', help='Sequence order of the configuration item.')
    font_style = fields.Selection(
        [('helvetica', 'Helvetica'), ('calibri', 'Calibri'), ('times', 'Times New Roman')],
        string='Font Style',
        default='helvetica',
        help='Font style for the overlay text.'
    )
    font_size = fields.Integer(string='Font Size', help='Font size for the overlay text.')
