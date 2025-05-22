from odoo import models, fields, api
from odoo.exceptions import UserError
from reportlab.lib.pagesizes import letter, legal, A3, A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import PyPDF2
from io import BytesIO
import base64
from odoo.modules import get_module_path

PAGE_SIZES = {
    "letter": letter,
    "legal": legal,
    "a3": A3,
    "a4": A4,
    "half_sheet_horizontal": (396, 306),
    "half_sheet_vertical": (306, 396),
}

class PrePrintedForm(models.Model):
    _name = "pre.printed.form"
    _description = "Pre‑Printed Form"

    name = fields.Char(
        string="Pre-printed Form Name",
        required=True,
        default=lambda self: self.env["ir.sequence"].next_by_code("pre.printed.form") or "New",
    )
    page_size = fields.Selection(
        selection=[
            ("letter", "Letter"),
            ("legal", "Legal"),
            ("a3", "A3"),
            ("a4", "A4"),
            ("half_sheet_horizontal", "Half Sheet Horizontal"),
            ("half_sheet_vertical", "Half Sheet vertical"),
        ],
        string="Page Size",
        required=True,
        default="letter",
        help="Page size for the pre-printed form.",
    )
    input_pdf_attachment_id = fields.Many2one(
        comodel_name="ir.attachment",
        string="Input PDF",
        required=True,
        domain=[("mimetype", "=", "application/pdf"), ("res_model", "=", False)],
        help="Select a PDF file that will serve as the input for overlay text.",
    )
    text_item_ids = fields.One2many(
        comodel_name="overlay.text.item",
        inverse_name="form_id",
        string="Text Items",
    )
    config_item_ids = fields.One2many(
        comodel_name="overlay.config.item",
        inverse_name="form_id",
        string="Config Items",
    )
    output_pdf_name = fields.Char(
        string="Output PDF Name",
        required=True,
        default=lambda self: f"{self.name}_output.pdf",
        help="Name for the generated PDF file.",
    )
    model_id = fields.Many2one(
        comodel_name="ir.model",
        string="Model",
        help="Select a model related to this pre-printed form.",
    )
    code = fields.Text(
        string="Custom Code",
        help="This field will be used to call a custom function that will return a list of x, y, and text",
    )

    @api.model
    def _register_fonts(self):
        try:
            module_path = get_module_path('pre-printed-forms-writer')
            font_folder = f"{module_path}/static/fonts/"

            # AgencyFB font variants
            pdfmetrics.registerFont(TTFont('AGENCYFB', font_folder + 'AGENCYFB.ttf'))
            pdfmetrics.registerFont(TTFont('AGENCYFB-Bold', font_folder + 'AGENCYFB-Bold.ttf'))
            pdfmetrics.registerFont(TTFont('AGENCYFB-Italic', font_folder + 'AGENCYFB-Italic.ttf'))
            pdfmetrics.registerFont(TTFont('AGENCYFB-BoldItalic', font_folder + 'AGENCYFB-BoldItalic.ttf'))

            # Calibri font variants
            pdfmetrics.registerFont(TTFont('Calibri', font_folder + 'CALIBRI.ttf'))
            pdfmetrics.registerFont(TTFont('Calibri-Bold', font_folder + 'CALIBRI-Bold.ttf'))
            pdfmetrics.registerFont(TTFont('Calibri-Italic', font_folder + 'CALIBRI-Italic.ttf'))
            pdfmetrics.registerFont(TTFont('Calibri-BoldItalic', font_folder + 'CALIBRI-BoldItalic.ttf'))

            # Arial font variants
            pdfmetrics.registerFont(TTFont('Arial', font_folder + 'ARIAL.ttf'))
            pdfmetrics.registerFont(TTFont('Arial-Bold', font_folder + 'ARIAL-Bold.ttf'))
            pdfmetrics.registerFont(TTFont('Arial-Italic', font_folder + 'ARIAL-Italic.ttf'))
            pdfmetrics.registerFont(TTFont('Arial-BoldItalic', font_folder + 'ARIAL-BoldItalic.ttf'))

        except Exception as e:
            self.env['ir.logging'].sudo().create({
                'name': 'Font Registration',
                'type': 'server',
                'level': 'warning',
                'message': f'Failed to register custom fonts: {str(e)}',
                'path': 'pre.printed.form',
                'func': '_register_fonts',
                'line': 1,
            })

    def upload_pdf(self, pdf_data, pdf_name):
        for record in self:
            if not pdf_data:
                raise UserError("Please upload a PDF file before processing.")
            attachment = self.env["ir.attachment"].create({
                "name": pdf_name,
                "type": "binary",
                "datas": pdf_data,
                "mimetype": "application/pdf",
                "res_model": self._name,
                "res_id": record.id,
            })
            record.input_pdf_attachment_id = attachment

    def process_action(self, record_id):
        self._register_fonts()
        record_container = self.env[self.model_id.model].search([("id", "=", record_id)], limit=1)
        if not record_container:
            raise UserError("Record not found")
        if not self.input_pdf_attachment_id:
            raise UserError("Please select a PDF file before processing.")

        input_pdf_stream = BytesIO(base64.b64decode(self.input_pdf_attachment_id.datas))
        input_pdf = PyPDF2.PdfFileReader(input_pdf_stream)

        buffer = BytesIO()
        overlay_pdf = canvas.Canvas(buffer, pagesize=PAGE_SIZES.get(self.page_size, letter))

        style_map = {
            "times": {
                "normal": "Times-Roman",
                "bold": "Times-Bold",
                "italic": "Times-Italic",
                "bold_italic": "Times-BoldItalic",
            },
            "helvetica": {
                "normal": "Helvetica",
                "bold": "Helvetica-Bold",
                "italic": "Helvetica-Oblique",
                "bold_italic": "Helvetica-BoldOblique",
            },
            "arial": {
                "normal": "Arial",
                "bold": "Arial-Bold",
                "italic": "Arial-Italic",
                "bold_italic": "Arial-BoldItalic",
            },
            "calibri": {
                "normal": "Calibri",
                "bold": "Calibri-Bold",
                "italic": "Calibri-Italic",
                "bold_italic": "Calibri-BoldItalic",
            },
            "agency": {
                "normal": "AGENCYFB",
                "bold": "AGENCYFB-Bold",
                "italic": "AGENCYFB-Italic",
                "bold_italic": "AGENCYFB-BoldItalic",
            },
            "courier": {
                "normal": "Courier",
                "bold": "Courier-Bold",
                "italic": "Courier-Oblique",
                "bold_italic": "Courier-BoldOblique",
            },
        }

        for item in self.text_item_ids:
            x = float(item.x)
            y = float(item.y)
            font_size = 12
            font_name = "Times-Roman"
            config = item.config_id
            underline = False
            if config:
                bold = getattr(config, 'bold', False)
                italic = getattr(config, 'italic', False)
                underline = getattr(config, 'underline', False)

                if bold and italic:
                    font_format_key = "bold_italic"
                elif bold:
                    font_format_key = "bold"
                elif italic:
                    font_format_key = "italic"
                else:
                    font_format_key = "normal"

                font_style_key = config.font_style or "times"
                font_name = style_map.get(font_style_key, style_map["times"]).get(font_format_key, "Times-Roman")
                font_size = config.font_size or 12

            try:
                overlay_pdf.setFont(font_name, font_size)
            except Exception:
                overlay_pdf.setFont("Times-Roman", font_size)

            text_to_draw = item.text
            if item.field_id and self.model_id:
                record_object = self.env[self.model_id.model].search([("id", "=", record_id)], limit=1)
                if record_object:
                    field_name = item.field_id.name
                    text_to_draw = getattr(record_object, field_name, item.text)
            text_to_draw = str(text_to_draw) if text_to_draw is not None else ""

            overlay_pdf.drawString(x, y, text_to_draw)

            if underline:
                text_width = overlay_pdf.stringWidth(text_to_draw, font_name, font_size)
                overlay_pdf.line(x, y - 2, x + text_width, y - 2)

        if self.code:
            try:
                items = eval(self.code)
                for item in items:
                    overlay_pdf.drawString(item["x"], item["y"], item["text"])
            except Exception as e:
                raise UserError(f"Error evaluating custom code: {e}")

        overlay_pdf.showPage()
        overlay_pdf.save()
        buffer.seek(0)
        overlay_pdf_stream = buffer.read()
        buffer.close()

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

        pdf_name = self.output_pdf_name or "test.pdf"
        attachment = self.env["ir.attachment"].create({
            "name": pdf_name,
            "type": "binary",
            "datas": base64.b64encode(pdf_data).decode("utf-8"),
            "mimetype": "application/pdf",
            "res_model": self._name,
            "res_id": self.id,
        })

        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{attachment.id}?download=true",
            "target": "self",
        }

    def create_contextual_action(self):
        IrActionsServer = self.env["ir.actions.server"]
        for rec in self:
            action_code = f"""action = None
for record in records:
    pre_printed_form_id = {rec.id}
    pre_printed_form = env['pre.printed.form'].search([('id', '=', pre_printed_form_id)], limit=1)
    action = pre_printed_form.process_action(record.id)
    break"""
            temp = IrActionsServer.create({
                "name": rec.name,
                "state": "code",
                "model_id": rec.model_id.id,
                "code": action_code,
            })
            temp.create_action()
