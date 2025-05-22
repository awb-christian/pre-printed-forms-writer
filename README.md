# Pre-Printed Forms Module for Odoo

This Odoo module allows users to create and manage pre-printed forms with customizable overlay text items, supporting multiple page sizes and advanced font styling including bold, italic, underline, and combinations using both built-in and custom TrueType fonts.

---

## Features

- Upload PDF templates as base forms.
- Add overlay text items positioned precisely on the form.
- Dynamic text rendering based on model fields.
- Supports multiple page sizes: Letter, Legal, A3, A4, Half-sheet formats.
- Custom font support with registration of TrueType fonts (e.g., Arial, Calibri, AgencyFB).
- Supports font styles: normal, bold, italic, bold-italic, underline.
- Generates downloadable PDF output with overlays merged.
- Create contextual server actions for automation.

---

## Installation

1. Place the module folder under your Odoo addons directory.
2. Add your custom font files (`.ttf`) in the module's `static/fonts` folder:
   - `AGENCYFB.ttf`, `AGENCYFB-Bold.ttf`, `AGENCYFB-Italic.ttf`, `AGENCYFB-BoldItalic.ttf`
   - `CALIBRI.ttf`, `CALIBRI-Bold.ttf`, `CALIBRI-Italic.ttf`, `CALIBRI-BoldItalic.ttf`
   - `ARIAL.ttf`, `ARIAL-Bold.ttf`, `ARIAL-Italic.ttf`, `ARIAL-BoldItalic.ttf`
3. Update your Odoo app list and install the module.
4. Ensure your PDF files are uploaded correctly through the provided interface.

---

## Usage

1. Create a new Pre-Printed Form record.
2. Upload a base PDF template.
3. Define overlay text items with their coordinates, font style, size, and formatting options.
4. Use dynamic fields to pull text from related models if needed.
5. Generate the output PDF with merged overlays.
6. (Optional) Create contextual server actions to automate processing on related records.

---

## Supported Fonts

- Built-in ReportLab fonts with styles for:
  - Times (Roman, Bold, Italic, BoldItalic)
  - Helvetica (Normal, Bold, Oblique, BoldOblique)
  - Courier (Normal, Bold, Oblique, BoldOblique)
- Custom fonts loaded via TTF files:
  - AgencyFB
  - Calibri
  - Arial

---

## Developer Notes

- The module registers custom fonts dynamically on PDF generation.
- Use exact PostScript font names in your font style configuration.
- Font format is now implemented with checkboxes allowing combinations of bold, italic, and underline.
- Underline is drawn manually using a line under the text.
- Custom code execution is supported to add arbitrary overlay texts via Python expressions (use with caution).
- Make sure all custom fonts are present in the `static/fonts` directory with correct filenames.

---

## Troubleshooting

- **Fonts not applied correctly?**  
  Ensure TTF files are properly named and placed in the `static/fonts` folder.  
  For built-in fonts (Times, Helvetica, Courier), no TTF registration is required.

- **PDF output issues?**  
  Verify that the base PDF and overlays do not have page size conflicts.  
  Confirm that your coordinates are correct for the selected page size.

- **Server errors on font registration?**  
  Check Odoo logs for permission issues or path problems with font files.

---


