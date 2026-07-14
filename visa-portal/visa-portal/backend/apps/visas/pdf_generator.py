from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from apps.visas.models import ApplicationData

class VisaPDFGenerator:
    def __init__(self, application):
        self.application = application

    def generate(self):
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, height - 50, f"Candidatura de Visto: {self.application.visa_type.name}")
        p.setFont("Helvetica", 12)
        p.drawString(50, height - 80, f"Candidato: {self.application.user.email}")
        p.drawString(50, height - 100, f"ID: {self.application.id}")

        y_position = height - 140
        for data in self.application.data.all():
            p.setFont("Helvetica-Bold", 10)
            p.drawString(50, y_position, f"{data.field.label}:")
            p.setFont("Helvetica", 10)
            value = data.get_decrypted_text() or (data.value_file.name if data.value_file else "N/A")
            p.drawString(50, y_position - 15, value)
            y_position -= 40

        p.save()
        buffer.seek(0)
        return buffer
