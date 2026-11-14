from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Patient

MEDICAL_FIELDS = ["blood_type", "allergies", "chronic_conditions"]
MEDICAL_ROLES = {"admin", "doctor", "nurse"}


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ["national_id", "first_name", "last_name", "date_of_birth", "gender",
                  "phone", "address"] + MEDICAL_FIELDS
        labels = {
            "first_name": _("First name"), "last_name": _("Last name"), "date_of_birth": _("Date of birth"),
            "gender": _("Gender"), "phone": _("Phone"), "address": _("Address"), "blood_type": _("Blood type"),
            "allergies": _("Allergies"), "chronic_conditions": _("Chronic conditions"),
        }
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "allergies": forms.Textarea(attrs={"rows": 2}),
            "chronic_conditions": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Receptionists register demographics only; medical fields are removed for them.
        if user is not None and user.role not in MEDICAL_ROLES:
            for f in MEDICAL_FIELDS:
                self.fields.pop(f)
