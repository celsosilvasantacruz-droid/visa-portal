from rest_framework import serializers
from .models import VisaType, Application, FormField, ApplicationData

class FormFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormField
        fields = ['id', 'label', 'field_type', 'is_required', 'placeholder', 'help_text', 'validation_regex', 'order']

class VisaTypeSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', read_only=True)
    class Meta:
        model = VisaType
        fields = ['id', 'name', 'country_name', 'description', 'price_service']

class ApplicationSerializer(serializers.ModelSerializer):
    visa_type_name = serializers.CharField(source='visa_type.name', read_only=True)
    class Meta:
        model = Application
        fields = ['id', 'visa_type', 'visa_type_name', 'status', 'pdf_generated', 'created_at']
        read_only_fields = ['id', 'status', 'pdf_generated', 'created_at']
