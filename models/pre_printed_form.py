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

# Define page sizes for PDF generation
PAGE_SIZES = {
    'letter': letter,
    'legal': legal,
    'a3': A3,
    'a4': A4,
    'half_sheet_horizontal': (396, 306),  # 5.5" x 8.5"
    'half_sheet_vertical': (306, 396),    # 8.5" x 5.5"
}


class PrePrintedForm(models.Model):
    """
    PrePrintedForm model manages pre-printed forms with overlay text items.
    """
    _name = 'pre.printed.form'
    _description = 'Pre‑Printed Form'

    # Field Definitions
    name = fields.Char(
        string='Pre-printed Form Name',
        required=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('pre.printed.form') or 'New'
    )
    page_size = fields.Selection(
        selection=[
            ('letter', 'Letter'),
            ('legal', 'Legal'),
            ('a3', 'A3'),
            ('a4', 'A4'),
            ('half sheet horizontal', 'Half Sheet Horizontal'),
            ('half sheet vertical', 'Half Sheet vertical')
        ],
        string='Page Size',
        required=True,
        default='letter',
        help='Page size for the pre-printed form.'
    )
    input_pdf_attachment_id = fields.Many2one(
        comodel_name='ir.attachment',
        string='Input PDF',
        required=True,
        domain=[('mimetype', '=', 'application/pdf')],
        help='Select a PDF file that will serve as the input for overlay text.'
    )
    text_item_ids = fields.One2many(
        comodel_name='overlay.text.item',
        inverse_name='form_id',
        string='Text Items'
    )
    config_item_ids = fields.One2many(
        comodel_name='overlay.config.item',
        inverse_name='form_id',
        string='Config Items'
    )
    output_pdf_name = fields.Char(
        string='Output PDF Name',
        required=True,
        default=lambda self: f"{self.name}_output.pdf",
        help='Name for the generated PDF file.'
    )
    model_id = fields.Many2one(
        comodel_name='ir.model',
        string='Model',
        help='Select a model related to this pre-printed form.'
    )

    def upload_pdf(self, pdf_data, pdf_name):
        """
        Uploads a PDF file and creates an attachment.

        :param pdf_data: Base64 encoded PDF data
        :param pdf_name: Name of the PDF file
        """
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

    def process_action(self, model_id=None):
        """
        Processes the pre-printed form by overlaying text items on the input PDF.

        :param model_id: Optional model ID for dynamic text replacement
        """
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
            overlay_pdf = canvas.Canvas(buffer, pagesize=PAGE_SIZES.get(record.page_size, letter))

            for item in record.text_item_ids:
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
                text_to_draw = item.text
                if item.field_id and model_id:
                    model = self.env[record.model_id.model].search([('id', '=', model_id)], limit=1)
                    if model:
                        field_name = item.field_id.name
                        text_to_draw = getattr(model, field_name, item.text)
                # Ensure text_to_draw is a string
                text_to_draw = str(text_to_draw) if text_to_draw is not None else ''

                overlay_pdf.drawString(x, y, text_to_draw)
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

            # Use the user-specified name for the PDF file, or default to 'text_items_overlay.pdf'
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