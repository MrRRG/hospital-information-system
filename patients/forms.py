from django import forms

from .models import Patient

MEDICAL_FIELDS = ["blood_type", "allergies", "chronic_conditions"]
MEDICAL_ROLES = {"admin", "doctor", "nurse"}


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ["national_id", "first_name", "last_name", "date_of_birth", "gender",
                  "phone", "address"] + MEDICAL_FIELDS
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
