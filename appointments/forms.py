from datetime import date

from django import forms
from django.utils.translation import gettext as _t
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from patients.models import Patient

from .models import Appointment


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["patient", "doctor", "date", "start_time", "reason"]
        labels = {"patient": _("Patient"), "doctor": _("Doctor"), "date": _("Date"), "reason": _("Reason")}
        widgets = {"date": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["patient"].queryset = Patient.objects.order_by("first_name", "last_name")
        self.fields["patient"].label_from_instance = lambda p: f"{p.mrn} - {p.full_name}"
        self.fields["doctor"].queryset = User.objects.filter(role="doctor", is_active=True)
        self.fields["start_time"].label = _("Time")

    def clean(self):
        data = super().clean()
        d, t, doctor = data.get("date"), data.get("start_time"), data.get("doctor")
        if d and d < date.today():
            self.add_error("date", _t("Choose today or a future date."))
        if d and t and doctor:
            clash = Appointment.objects.filter(doctor=doctor, date=d, start_time=t).exclude(
                status__in=["cancelled", "no_show"]).exclude(pk=self.instance.pk)
            if clash.exists():
                self.add_error("start_time", _t("%(doctor)s already has an appointment at %(time)s. Pick another time or doctor.")
                               % {"doctor": doctor.get_full_name(), "time": f"{t:%H:%M}"})
        return data
