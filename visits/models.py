from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Visit(models.Model):
    patient = models.ForeignKey("patients.Patient", on_delete=models.PROTECT, related_name="visits")
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT,
                               limit_choices_to={"role": "doctor"}, related_name="visits")
    appointment = models.OneToOneField("appointments.Appointment", null=True, blank=True,
                                       on_delete=models.SET_NULL, related_name="visit")
    complaint = models.CharField(_("Reason for visit"), max_length=200)
    # Vital signs (nurse or doctor)
    temperature = models.DecimalField(_("Temperature (C)"), max_digits=4, decimal_places=1, null=True, blank=True,
                                      validators=[MinValueValidator(30), MaxValueValidator(45)])
    systolic = models.PositiveSmallIntegerField(_("Blood pressure - systolic"), null=True, blank=True,
                                                validators=[MinValueValidator(50), MaxValueValidator(260)])
    diastolic = models.PositiveSmallIntegerField(_("Blood pressure - diastolic"), null=True, blank=True,
                                                 validators=[MinValueValidator(30), MaxValueValidator(160)])
    heart_rate = models.PositiveSmallIntegerField(_("Heart rate (bpm)"), null=True, blank=True,
                                                  validators=[MinValueValidator(20), MaxValueValidator(250)])
    weight_kg = models.DecimalField(_("Weight (kg)"), max_digits=5, decimal_places=1, null=True, blank=True,
                                    validators=[MinValueValidator(1), MaxValueValidator(400)])
    # Clinical notes (doctor only)
    diagnosis = models.TextField(blank=True)
    treatment_plan = models.TextField(blank=True)
    notes = models.TextField(_("Doctor's notes"), blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL,
                                   related_name="visits_created")
    visit_time = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-visit_time"]

    @property
    def blood_pressure(self):
        return f"{self.systolic}/{self.diastolic}" if self.systolic and self.diastolic else ""

    def __str__(self):
        return f"Visit of {self.patient.full_name} on {self.visit_time:%Y-%m-%d}"
