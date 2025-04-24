# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class OverlayTestItem(models.Model):
    _name = 'overlay.test.item'
    _description = 'Overlay Test Item'
    _order = 'sequence, id'

    name = fields.Char(string='Item Name', required=True)
    form_id = fields.Many2one(
        comodel_name='pre.printed.form',
        string='Pre‑Printed Form',
        ondelete='cascade'
    )
    notes = fields.Text(string='Notes')
    sequence = fields.Integer(string='Sequence', help='Sequence order of the test item.')
    x = fields.Float(string='X Coordinate', help='X position on the form.')
    y = fields.Float(string='Y Coordinate', help='Y position on the form.')
    text = fields.Char(string='Text', help='Text to overlay on the form.')
    config_id = fields.Many2one(
        comodel_name='overlay.config.item',
        string='Config Item',
        help='Configuration for this test item.'
    )
    field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string='Field',
        help='Select a field from the model associated with the pre-printed form.'
    )

    @api.constrains('x', 'y')
    def _check_coordinates(self):
        for record in self:
            if record.x < 0 or record.y < 0:
                raise ValidationError("Coordinates must be non-negative.")

    def name_get(self):
        return [(rec.id, f"{rec.name} ({rec.x:.1f}, {rec.y:.1f})") for rec in self]

