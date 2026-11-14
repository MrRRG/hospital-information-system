from django.contrib.auth.decorators import login_required
from datetime import date, timedelta

from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext as _t
from django.utils.translation import gettext_lazy as _

# Modules each role can open. "ready" turns True as we build each module.
MODULES = [
    {"key": "patients", "title": _("Patients"), "text": _("Register and search patient records."),
     "roles": {"admin", "doctor", "nurse", "receptionist"}, "ready": True, "url": "patient_list"},
    {"key": "appointments", "title": _("Appointments"), "text": _("Book and manage clinic appointments."),
     "roles": {"admin", "doctor", "receptionist"}, "ready": True, "url": "appointment_list"},
    {"key": "visits", "title": _("Visits and notes"), "text": _("Record visits and medical notes."),
     "roles": {"admin", "doctor", "nurse"}, "ready": True, "url": "visit_list"},
    {"key": "audit", "title": _("Audit log"), "text": _("See who opened or changed a record."),
     "roles": {"admin"}, "ready": True, "url": "audit_list"},
]


@login_required
def dashboard(request):
    from appointments.models import Appointment
    from patients.models import Patient
    from visits.models import Visit

    role, today = request.user.role, date.today()
    stats = [(_t("Patients registered"), Patient.objects.count())]
    if role in ("admin", "doctor", "receptionist"):
        appts = Appointment.objects.filter(date=today)
        if role == "doctor":
            appts = appts.filter(doctor=request.user)
        stats.append((_t("Appointments today"), appts.exclude(status__in=["cancelled", "no_show"]).count()))
        stats.append((_t("Waiting (checked in)"), appts.filter(status="checked_in").count()))
    if role in ("admin", "doctor", "nurse"):
        week = Visit.objects.filter(visit_time__date__gte=today - timedelta(days=6)).count()
        stats.append((_t("Visits in the last 7 days"), week))
    modules = [m for m in MODULES if role in m["roles"]]
    hour = timezone.localtime().hour
    greeting = _t("Good morning") if hour < 12 else _t("Good afternoon") if hour < 17 else _t("Good evening")
    return render(request, "dashboard.html", {"modules": modules, "stats": stats, "greeting": greeting})
