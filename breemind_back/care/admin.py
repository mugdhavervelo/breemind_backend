from django.contrib import admin

from .models import Appointment
from .models import Note
from .models import Patient
from .models import PlanOfCare


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "first_name",
        "last_name",
        "whatsapp_number",
        "is_active",
        "created_at",
    )
    search_fields = ("first_name", "last_name", "whatsapp_number", "email")
    list_filter = ("is_active",)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "patient",
        "doctor",
        "scheduled_start_at",
        "duration_minutes",
        "status",
    )
    list_filter = ("status", "doctor")
    search_fields = ("patient__first_name", "patient__last_name", "doctor__username")


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "author", "note_type", "is_locked", "created_at")
    list_filter = ("note_type", "is_locked")
    search_fields = ("patient__first_name", "patient__last_name", "author__username")


@admin.register(PlanOfCare)
class PlanOfCareAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "title", "status", "start_date", "end_date")
    list_filter = ("status",)
    search_fields = ("patient__first_name", "patient__last_name", "title")
