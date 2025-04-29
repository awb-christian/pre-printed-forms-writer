# -*- coding: utf-8 -*-
from odoo import models, fields

class OverlayConfigurationItem(models.Model):
    """
    OverlayConfigurationItem model manages configuration settings for overlay text items.
    """
    _name = 'overlay.config.item'
    _description = 'Overlay Configuration Item'

    # Field Definitions
    name = fields.Char(string='Config Name', required=True)
    form_id = fields.Many2one(
        comodel_name='pre.printed.form',
        string='Pre‑Printed Form',
        ondelete='cascade'
    )
    font_style = fields.Selection([
        ('helvetica', 'Helvetica'), 
        ('calibri', 'Calibri'), 
        ('times', 'Times New Roman'),
        ('agency', 'Agency FB'),
        ('arial', 'Arial')],
        string='Font Style',
        default='times',
        help='Font style for the overlay text.'
    )
    font_size = fields.Integer(string='Font Size', help='Font size for the overlay text.')
    font_format = fields.Selection([
        ('normal', 'Normal'),
        ('bold', 'Bold'),
        ('italic', 'Italic'),
        ('underline', 'Underline')],
        string='Font Format',
        default='normal',
        help='Font format for the overlay text.'
    )

    
