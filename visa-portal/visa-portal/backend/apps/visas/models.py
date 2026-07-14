from django.db import models
from django.conf import settings
from apps.core.encryption import encrypt_data, decrypt_data

class Country(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=2, unique=True)
    flag_url = models.URLField(blank=True, null=True)
    embassy_email = models.EmailField(blank=True, null=True)
    def __str__(self): return self.name

class VisaType(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='visas')
    name = models.CharField(max_length=100)
    description = models.TextField()
    price_service = models.DecimalField(max_digits=10, decimal_places=2, default=29.90)
    is_active = models.BooleanField(default=True)
    def __str__(self): return f"{self.country.name} - {self.name}"

class FormField(models.Model):
    FIELD_TYPES = [('text', 'Texto'), ('email', 'Email'), ('date', 'Data'), ('number', 'Número'), ('file', 'Documento'), ('select', 'Seleção'), ('textarea', 'Texto Longo')]
    visa_type = models.ForeignKey(VisaType, on_delete=models.CASCADE, related_name='fields')
    label = models.CharField(max_length=200)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    is_required = models.BooleanField(default=True)
    placeholder = models.CharField(max_length=200, blank=True)
    help_text = models.TextField(blank=True)
    validation_regex = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)
    class Meta: ordering = ['order']

class Application(models.Model):
    STATUS_CHOICES = [('draft', 'Rascunho'), ('submitted', 'Submetido'), ('processing', 'Em Processamento'), ('completed', 'Concluído'), ('rejected', 'Rejeitado')]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    visa_type = models.ForeignKey(VisaType, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    pdf_generated = models.FileField(upload_to='pdfs/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

def application_file_path(instance, filename):
    return f"documents/app_{instance.application.id}/{filename}"

class ApplicationData(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='data')
    field = models.ForeignKey(FormField, on_delete=models.CASCADE)
    value_text = models.TextField(blank=True, null=True)
    value_file = models.FileField(upload_to=application_file_path, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.value_text and not str(self.value_text).startswith('ENC:'):
            self.value_text = encrypt_data(self.value_text)
        super().save(*args, **kwargs)

    def get_decrypted_text(self):
        if self.value_text and str(self.value_text).startswith('ENC:'):
            return decrypt_data(self.value_text)
        return self.value_text
