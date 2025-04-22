from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

def generate_pdf():
    c = canvas.Canvas("example.pdf", pagesize=letter)
    c.setFont("Helvetica", 12)  # Set font style and size
    c.drawString(100, 750, "Hello, World!")  # Draw text on the PDF
    c.save()
