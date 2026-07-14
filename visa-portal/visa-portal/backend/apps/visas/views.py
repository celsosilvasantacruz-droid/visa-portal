import json
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import VisaType, Application, ApplicationData, FormField
from .serializers import VisaTypeSerializer, ApplicationSerializer, FormFieldSerializer
from apps.core.tasks import generate_and_send_pdf_task, send_to_embassy_task

class VisaTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = VisaType.objects.filter(is_active=True).select_related('country')
    serializer_class = VisaTypeSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'])
    def fields(self, request, pk=None):
        fields = self.get_object().fields.all()
        return Response(FormFieldSerializer(fields, many=True).data)

class ApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Application.objects.filter(user=self.request.user).select_related('visa_type', 'visa_type__country')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, status='draft')

    @action(detail=True, methods=['post'])
    def submit_data(self, request, pk=None):
        application = self.get_object()
        if application.status != 'draft':
            return Response({'error': 'Esta candidatura já foi submetida.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                fields_data = json.loads(request.data.get('fields', '[]'))
                for field_data in fields_data:
                    field = get_object_or_404(FormField, id=field_data['field_id'], visa_type=application.visa_type)
                    ApplicationData.objects.update_or_create(
                        application=application, field=field,
                        defaults={'value_text': field_data.get('value_text')}
                    )

                for field in application.visa_type.fields.filter(field_type='file'):
                    file_obj = request.FILES.get(f'field_{field.id}')
                    if file_obj:
                        if file_obj.size > 5 * 1024 * 1024:
                            raise ValueError(f"O ficheiro {file_obj.name} excede o limite de 5MB.")
                        if not file_obj.content_type.startswith(('image/', 'application/pdf')):
                            raise ValueError(f"Tipo de ficheiro inválido para {field.label}.")
                        ApplicationData.objects.update_or_create(
                            application=application, field=field,
                            defaults={'value_file': file_obj}
                        )

                application.status = 'submitted'
                application.save()

            generate_and_send_pdf_task.delay(application.id)
            return Response({'status': 'Candidatura submetida. Processamento em background.', 'application_id': application.id})

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except json.JSONDecodeError:
            return Response({'error': 'Formato de dados inválido.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({'error': 'Erro interno ao processar.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def send_to_embassy(self, request, pk=None):
        application = self.get_object()
        if application.status not in ['completed', 'processing'] or not application.pdf_generated:
            return Response({'error': 'A candidatura não está pronta ou o PDF não foi gerado.'}, status=status.HTTP_400_BAD_REQUEST)
        send_to_embassy_task.delay(application.id)
        return Response({'status': 'Envio para a embaixada iniciado.'})
