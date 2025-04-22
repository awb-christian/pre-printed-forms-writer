# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
import base64

class PrePrintedForm(models.Model):
    _name = 'pre.printed.form'
    _description = 'Pre‑Printed Form'

    name = fields.Char(string='Form Name', required=True)
    description = fields.Text(string='Description')
    page_size = fields.Selection([
        ('letter', 'Letter'), 
        ('legal', 'Legal'), 
        ('a3', 'A3'),
        ('a4', 'A4'),
        ('half sheet horizontal', 'Half Sheet Horizontal'),
        ('half sheet vertical', 'Half Sheet vertical')],
        string='Font Style',
        default='letter',
        help='Page size for the pre-printed form.'
    )
    input_pdf_attachment_id = fields.Many2one(
        comodel_name='ir.attachment',
        string='Input PDF',
        domain=[('mimetype', '=', 'application/pdf')],
        help='Select a PDF file that will serve as the input for overlay text.'
    )
    test_item_ids = fields.One2many(
        comodel_name='overlay.test.item',
        inverse_name='form_id',
        string='Test Items'
    )
    config_item_ids = fields.One2many(
        comodel_name='overlay.config.item',
        inverse_name='form_id',
        string='Config Items'
    )

    def upload_pdf(self, pdf_data, pdf_name):
        for record in self:
            if not pdf_data:
                raise UserError("Please upload a PDF file before processing.")
            
            # Create an attachment with the uploaded PDF
            attachment = self.env['ir.attachment'].create({
                'name': pdf_name,
                'type': 'binary',
                'datas': pdf_data,
                'mimetype': 'application/pdf',
                'res_model': self._name,
                'res_id': record.id,
            })
            # Link the attachment to the input_pdf_attachment_id field
            record.input_pdf_attachment_id = attachment

    def process_action(self):
        for record in self:
            if not record.input_pdf_attachment_id:
                raise UserError("Please select a PDF file before processing.")
            
            # Process the selected PDF
            pdf_content = record.input_pdf_attachment_id.datas
            # Add your processing logic here

    def process_action(self):
        pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 144] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 55 >>\nstream\nBT\n/F1 24 Tf\n100 100 Td\n(Hello, World!) Tj\nET\nendstream\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"
        
        attachment = self.env['ir.attachment'].create({
            'name': 'hello_world.pdf',
            'type': 'binary',
            'datas': base64.b64encode(pdf_content).decode('utf-8'),
            'mimetype': 'application/pdf',
            'res_model': self._name,
            'res_id': self.id,
        })
