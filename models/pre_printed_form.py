# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from reportlab.lib.pagesizes import letter, legal, A3, A4
from reportlab.pdfgen import canvas
from io import BytesIO
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
    # Define page size mapping
        page_sizes = {
            'letter': letter,
            'legal': legal,
            'a3': A3,
            'a4': A4,
            'half sheet horizontal': (396, 306),  # 5.5" x 8.5"
            'half sheet vertical': (306, 396),    # 8.5" x 5.5"
        }

        for record in self:
            page_size = page_sizes.get(record.page_size, letter)
            buffer = BytesIO()
            pdf = canvas.Canvas(buffer, pagesize=page_size)

            for item in record.test_item_ids:
                x = float(item.x)
                y = float(item.y)

                # Default font values
                font_name = 'Times-Roman'
                font_size = 12

                config = item.config_id
                if config:
                    style_map = {
                        'times': 'Times-Roman',
                        'helvetica': 'Helvetica',
                        'arial': 'Helvetica',
                        'calibri': 'Helvetica',
                        'agency': 'Helvetica'
                    }

                    base_font = style_map.get(config.font_style, 'Times-Roman')
                    suffix = ''
                    if config.font_format == 'bold':
                        suffix = '-Bold'
                    elif config.font_format == 'italic':
                        suffix = '-Oblique'

                    font_name = f"{base_font}{suffix}"
                    font_size = config.font_size or 12

                pdf.setFont(font_name, font_size)
                pdf.drawString(x, y, item.text)

                # Simulate underline if needed
                if config and config.font_format == 'underline':
                    text_width = pdf.stringWidth(item.text, font_name, font_size)
                    pdf.line(x, y - 2, x + text_width, y - 2)

            pdf.showPage()
            pdf.save()

            buffer.seek(0)
            pdf_data = buffer.read()
            buffer.close()

            attachment = self.env['ir.attachment'].create({
                'name': 'test_items.pdf',
                'type': 'binary',
                'datas': base64.b64encode(pdf_data).decode('utf-8'),
                'mimetype': 'application/pdf',
                'res_model': self._name,
                'res_id': record.id,
            })

            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true',
                'target': 'self',
            }