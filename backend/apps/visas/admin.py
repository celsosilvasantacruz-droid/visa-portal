from django.contrib import admin
from .models import Country, VisaType, FormField, Application, ApplicationData


class FormFieldInline(admin.TabularInline):
    model = FormField
    extra = 1


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'embassy_email')
    search_fields = ('name', 'code')


@admin.register(VisaType)
class VisaTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'price_service', 'is_active')
    list_filter = ('country', 'is_active')
    inlines = [FormFieldInline]


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'visa_type', 'status', 'created_at')
    list_filter = ('status', 'visa_type')
    search_fields = ('user__email',)


admin.site.register(ApplicationData)
