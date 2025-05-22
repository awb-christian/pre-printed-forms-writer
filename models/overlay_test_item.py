from odoo import models, fields, api
from odoo.exceptions import ValidationError

class OverlayTextItem(models.Model):
    _name = 'overlay.text.item'
    _description = 'Overlay Text Item'
    _order = 'id'

    name = fields.Char(string='Item Name', required=True)
    form_id = fields.Many2one(
        comodel_name='pre.printed.form',
        string='Pre-Printed Form',
        ondelete='cascade',
        required=True,
    )
    x = fields.Float(string='X Coordinate', required=True)
    y = fields.Float(string='Y Coordinate', required=True)
    text = fields.Char(string='Fallback/Static Text')
    config_id = fields.Many2one(
        comodel_name='overlay.config.item',
        string='Config Item',
    )
    field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string='Dynamic Text (From Field)',
    )

    @api.constrains('x', 'y')
    def _check_coordinates(self):
        for record in self:
            if record.x < 0 or record.y < 0:
                raise ValidationError("Coordinates must be non-negative.")

    def name_get(self):
        return [(rec.id, f"{rec.name} ({rec.x:.1f}, {rec.y:.1f})") for rec in self]
