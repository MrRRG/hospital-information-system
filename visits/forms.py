from django import forms
from django.utils.translation import gettext as _t
from django.utils.translation import gettext_lazy as _

from .models import Visit

VITALS = ["temperature", "systolic", "diastolic", "heart_rate", "weight_kg"]
CLINICAL = ["diagnosis", "treatment_plan", "notes"]


class VisitForm(forms.ModelForm):
    class Meta:
        model = Visit
        fields = ["complaint"] + VITALS + CLINICAL
        labels = {"diagnosis": _("Diagnosis"), "treatment_plan": _("Treatment plan")}
        widgets = {f: forms.Textarea(attrs={"rows": 3}) for f in CLINICAL}

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Nurses record the complaint and vital signs. Diagnosis and plan belong to the doctor.
        if user is not None and user.role == "nurse":
            for f in CLINICAL:
                self.fields.pop(f)

    def clean(self):
        data = super().clean()
        s, d = data.get("systolic"), data.get("diastolic")
        if (s and not d) or (d and not s):
            self.add_error("diastolic", _t("Enter both blood pressure numbers, or leave both empty."))
        elif s and d and s <= d:
            self.add_error("systolic", _t("Systolic must be higher than diastolic."))
        return data
