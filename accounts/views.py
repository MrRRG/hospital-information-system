from django.contrib.auth.decorators import login_required
from datetime import date, timedelta

from django.shortcuts import render
from django.utils import timezone

# Modules each role can open. "ready" turns True as we build each module.
MODULES = [
    {"key": "patients", "title": "Patients", "text": "Register and search patient records.",
     "roles": {"admin", "doctor", "nurse", "receptionist"}, "ready": True, "url": "patient_list"},
    {"key": "appointments", "title": "Appointments", "text": "Book and manage clinic appointments.",
     "roles": {"admin", "doctor", "receptionist"}, "ready": True, "url": "appointment_list"},
    {"key": "visits", "title": "Visits and notes", "text": "Record visits and medical notes.",
     "roles": {"admin", "doctor", "nurse"}, "ready": True, "url": "visit_list"},
    {"key": "audit", "title": "Audit log", "text": "See who opened or changed a record.",
     "roles": {"admin"}, "ready": True, "url": "audit_list"},
]


@login_required
def dashboard(request):
    from appointments.models import Appointment
    from patients.models import Patient
    from visits.models import Visit

    role, today = request.user.role, date.today()
    stats = [("Patients registered", Patient.objects.count())]
    if role in ("admin", "doctor", "receptionist"):
        appts = Appointment.objects.filter(date=today)
        if role == "doctor":
            appts = appts.filter(doctor=request.user)
        stats.append(("Appointments today", appts.exclude(status__in=["cancelled", "no_show"]).count()))
        stats.append(("Waiting (checked in)", appts.filter(status="checked_in").count()))
    if role in ("admin", "doctor", "nurse"):
        week = Visit.objects.filter(visit_time__date__gte=today - timedelta(days=6)).count()
        stats.append(("Visits in the last 7 days", week))
    modules = [m for m in MODULES if role in m["roles"]]
    hour = timezone.localtime().hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"
    return render(request, "dashboard.html", {"modules": modules, "stats": stats, "greeting": greeting})
