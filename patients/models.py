from datetime import date

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models

national_id_validator = RegexValidator(
    r"^[12]\d{9}$", "Enter a 10-digit National ID or Iqama number starting with 1 or 2."
)


class Patient(models.Model):
    class Gender(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"

    class BloodType(models.TextChoices):
        A_POS = "A+", "A+"
        A_NEG = "A-", "A-"
        B_POS = "B+", "B+"
        B_NEG = "B-", "B-"
        AB_POS = "AB+", "AB+"
        AB_NEG = "AB-", "AB-"
        O_POS = "O+", "O+"
        O_NEG = "O-", "O-"

    mrn = models.CharField("File number", max_length=12, unique=True, null=True, editable=False)
    national_id = models.CharField("National ID / Iqama", max_length=10, unique=True,
                                   validators=[national_id_validator])
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=Gender.choices)
    phone = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=200, blank=True)
    # Medical information: only doctors, nurses and admins can see or edit it.
    blood_type = models.CharField(max_length=3, choices=BloodType.choices, blank=True)
    allergies = models.TextField(blank=True)
    chronic_conditions = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL,
                                   related_name="patients_created")

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.mrn:  # file number is made from the row id: P-000001
            self.mrn = f"P-{self.pk:06d}"
            super().save(update_fields=["mrn"])

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        t = date.today()
        d = self.date_of_birth
        return t.year - d.year - ((t.month, t.day) < (d.month, d.day))

    def __str__(self):
        return f"{self.mrn} - {self.full_name}"
