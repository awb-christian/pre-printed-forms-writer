# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

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

    # model_ids = fields.One2many()

    @api.model
    def fetch_sales_data(self):
        sales_orders = self.env['sale.order'].search([])
        for order in sales_orders:
            _logger.debug(f"MODELS: {order.name, order.amount_total}")

    @api.model
    def fetch_accounting_data(self):
        invoices = self.env['account.move'].search([('move_type', '=', 'out_invoice')])
        for invoice in invoices:
            print(invoice.name, invoice.amount_total)
