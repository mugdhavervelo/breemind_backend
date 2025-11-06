from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F
from django.db.models import Q
from django.utils import timezone

from breemind_back.users.models import BaseModel


class Patient(BaseModel):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    whatsapp_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self) -> str:
        return self.full_name or f"Patient {self.pk}"


class Appointment(BaseModel):
    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Scheduled"
        COMPLETED = "COMPLETED", "Completed"
        CANCELED = "CANCELED", "Canceled"
        NO_SHOW = "NO_SHOW", "No show"
        RESCHEDULED = "RESCHEDULED", "Rescheduled"

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="appointments_as_doctor",
    )
    scheduled_start_at = models.DateTimeField()
    duration_minutes = models.PositiveSmallIntegerField(default=60)
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.SCHEDULED,
    )
    notes_summary = models.CharField(max_length=255, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="appointment_duration_gt_zero",
                condition=Q(duration_minutes__gt=0),
            ),
        ]

    @property
    def scheduled_end_at(self):
        return self.scheduled_start_at + timedelta(minutes=int(self.duration_minutes))

    @property
    def is_today(self) -> bool:
        now = timezone.now()
        return self.scheduled_start_at.date() == now.date()

    def __str__(self) -> str:
        return (
            f"{self.patient.full_name} with {self.doctor} at {self.scheduled_start_at}"
        )


class Note(BaseModel):
    class NoteType(models.TextChoices):
        GENERAL = "GENERAL", "General"
        SOAP = "SOAP", "SOAP"
        DIAGNOSIS = "DIAGNOSIS", "Diagnosis"
        PROGRESS = "PROGRESS", "Progress"

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="notes")
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name="notes",
        blank=True,
        null=True,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notes",
    )
    note_type = models.CharField(max_length=16, choices=NoteType.choices)
    content = models.TextField()
    is_locked = models.BooleanField(default=False)

    def clean(self):
        super().clean()
        if self.appointment and self.appointment.patient_id != self.patient_id:
            raise ValidationError("Appointment patient does not match note patient.")

    def __str__(self) -> str:
        return f"{self.get_note_type_display()} note for {self.patient.full_name}"


class PlanOfCare(BaseModel):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        COMPLETED = "COMPLETED", "Completed"
        ARCHIVED = "ARCHIVED", "Archived"

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="plans_of_care",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="plans_created",
    )
    title = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    goals = models.JSONField(default=dict, blank=True)
    review_date = models.DateField(blank=True, null=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="planofcare_start_before_end_or_null",
                condition=Q(end_date__isnull=True) | Q(start_date__lt=F("end_date")),
            ),
            models.UniqueConstraint(
                fields=["patient"],
                condition=Q(status="ACTIVE"),
                name="unique_active_plan_per_patient",
            ),
        ]

    def __str__(self) -> str:
        return f"PlanOfCare({self.patient.full_name} - {self.title})"
