# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class OverlayTextItem(models.Model):
    """
    OverlayTextItem model manages text items that overlay on pre-printed forms.
    """
    _name = 'overlay.text.item'
    _description = 'Overlay Text Item'
    _order = 'id'

    # Field Definitions
    name = fields.Char(string='Item Name', required=True)
    form_id = fields.Many2one(
        comodel_name='pre.printed.form',
        string='Pre‑Printed Form',
        ondelete='cascade'
    )
    x = fields.Float(string='X Coordinate', help='X position on the form.')
    y = fields.Float(string='Y Coordinate', help='Y position on the form.')
    text = fields.Char(string='Text', help='Text to overlay on the form.')
    config_id = fields.Many2one(
        comodel_name='overlay.config.item',
        string='Config Item',
        help='Configuration for this text item.'
    )
    field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string='Field',
        help='Select a field from the model associated with the pre-printed form.'
    )

    @api.constrains('x', 'y')
    def _check_coordinates(self):
        """
        Constraint to ensure coordinates are non-negative.
        """
        for record in self:
            if record.x < 0 or record.y < 0:
                raise ValidationError("Coordinates must be non-negative.")

    def name_get(self):
        """
        Returns a custom display name for records, including coordinates.
        """
        return [(rec.id, f"{rec.name} ({rec.x:.1f}, {rec.y:.1f})") for rec in self]

