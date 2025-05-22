from odoo import models, fields

class OverlayConfigurationItem(models.Model):
    _name = 'overlay.config.item'
    _description = 'Overlay Configuration Item'

    name = fields.Char(string='Config Name', required=True)
    form_id = fields.Many2one(
        comodel_name='pre.printed.form',
        string='Pre-Printed Form',
        ondelete='cascade',
        required=True,
    )
    font_style = fields.Selection([
        ('times', 'Times New Roman'),
        ('agency', 'Agency FB'),
        ('arial', 'Arial'),
        ('calibri', 'Calibri'),
        ('courier', 'Courier'),
        ('helvetica', 'Helvetica')],
        string='Font Style',
        default='times',
        required=True,
        help='Font style for the overlay text.'
    )
    font_size = fields.Integer(string='Font Size', required=True, help='Font size for the overlay text.')
    bold = fields.Boolean(string='Bold', help='Apply Bold font format for the overlay text.')
    italic = fields.Boolean(string='Italic', help='Apply Italic/Oblique font format for the overlay text.')
    underline = fields.Boolean(string='Underline', help='Apply Underline font format for the overlay text.')
