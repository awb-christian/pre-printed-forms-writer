# -*- coding: utf-8 -*-
from odoo import models, fields

class OverlayTestItem(models.Model):
    _name = 'overlay.test.item'
    _description = 'Overlay Test Item'

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
