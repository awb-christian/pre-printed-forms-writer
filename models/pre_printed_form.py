# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from reportlab.lib.pagesizes import letter, legal, A3, A4
from reportlab.pdfgen import canvas
import PyPDF2
from io import BytesIO
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import base64
from odoo.modules.module import get_module_resource

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
        string='Page Size',
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
    output_pdf_name = fields.Char(string='Output PDF Name', help='Name for the generated PDF file.')

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

        # Get the absolute path to the font file
        font_path = get_module_resource('pre-printed-forms-writer', 'static/fonts', 'AGENCYB.TTF')

        # Register custom fonts
        pdfmetrics.registerFont(TTFont('AgencyFB', font_path))
        pdfmetrics.registerFont(TTFont('AgencyFB-Bold', font_path))  # Register the same font for bold if no separate bold TTF is available

        for record in self:
            if not record.input_pdf_attachment_id:
                raise UserError("Please select a PDF file before processing.")

            # Read the uploaded PDF
            input_pdf_stream = BytesIO(base64.b64decode(record.input_pdf_attachment_id.datas))
            input_pdf = PyPDF2.PdfFileReader(input_pdf_stream)

            # Create a new PDF to overlay text
            buffer = BytesIO()
            overlay_pdf = canvas.Canvas(buffer, pagesize=page_sizes.get(record.page_size, letter))

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
                        'agency': 'AgencyFB'  # Use the registered custom font
                    }

                    base_font = style_map.get(config.font_style, 'Times-Roman')
                    suffix = ''
                    if config.font_format == 'bold':
                        suffix = '-Bold'
                    elif config.font_format == 'italic':
                        suffix = '-Oblique'

                    font_name = f"{base_font}{suffix}"
                    font_size = config.font_size or 12

                overlay_pdf.setFont(font_name, font_size)
                overlay_pdf.drawString(x, y, item.text)

                # Simulate underline if needed
                if config and config.font_format == 'underline':
                    text_width = overlay_pdf.stringWidth(item.text, font_name, font_size)
                    overlay_pdf.line(x, y - 2, x + text_width, y - 2)

            overlay_pdf.showPage()
            overlay_pdf.save()

            buffer.seek(0)
            overlay_pdf_stream = buffer.read()
            buffer.close()

            # Merge the overlay with the input PDF
            output_pdf_stream = BytesIO()
            output_pdf = PyPDF2.PdfFileWriter()

            for page_number in range(len(input_pdf.pages)):
                page = input_pdf.getPage(page_number)
                overlay_page = PyPDF2.PdfFileReader(BytesIO(overlay_pdf_stream)).getPage(0)
                page.mergePage(overlay_page)
                output_pdf.addPage(page)

            output_pdf.write(output_pdf_stream)
            output_pdf_stream.seek(0)
            pdf_data = output_pdf_stream.read()
            output_pdf_stream.close()

            # Use the user-specified name for the PDF file, or default to 'test_items_overlay.pdf'
            pdf_name = record.output_pdf_name or 'test.pdf'

            # Create attachment
            attachment = self.env['ir.attachment'].create({
                'name': pdf_name,
                'type': 'binary',
                'datas': base64.b64encode(pdf_data).decode('utf-8'),
                'mimetype': 'application/pdf',
                'res_model': self._name,
                'res_id': record.id,
            })

            # Return an action to download the PDF
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true',
                'target': 'self',
            }