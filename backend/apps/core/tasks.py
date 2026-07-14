from celery import shared_task
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from django.conf import settings
from apps.visas.models import Application
from apps.visas.pdf_generator import VisaPDFGenerator

@shared_task(bind=True, max_retries=3)
def generate_and_send_pdf_task(self, application_id):
    try:
        application = Application.objects.select_related('visa_type', 'user').get(id=application_id)
        pdf_buffer = VisaPDFGenerator(application).generate()
        filename = f"visa_app_{application.id}.pdf"
        application.pdf_generated.save(filename, ContentFile(pdf_buffer.getvalue()), save=True)
        application.status = 'processing'
        application.save()
        return f"PDF gerado: {application_id}"
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)

@shared_task
def send_to_embassy_task(application_id):
    application = Application.objects.select_related('visa_type__country').get(id=application_id)
    embassy_email = application.visa_type.country.embassy_email
    if not embassy_email: return "Email da embaixada não configurado."

    email = EmailMessage(
        subject=f"Nova Candidatura de Visto - {application.user.email}",
        body=f"Em anexo segue o PDF da candidatura #{application.id}.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[embassy_email],
    )
    email.attach_file(application.pdf_generated.path)
    email.send()
    application.status = 'completed'
    application.save()
    return "Enviado para a embaixada."
