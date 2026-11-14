from datetime import date, timedelta

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.models import User
from accounts.permissions import role_required
from audit.utils import record

from .forms import AppointmentForm
from .models import Appointment

# Who may move an appointment to which status.
STATUS_RIGHTS = {
    "receptionist": {"checked_in", "cancelled", "no_show"},
    "doctor": {"completed"},
    "admin": {"checked_in", "cancelled", "no_show", "completed"},
}


@role_required("doctor", "receptionist")
def appointment_list(request):
    try:
        day = date.fromisoformat(request.GET.get("date", ""))
    except ValueError:
        day = date.today()
    items = Appointment.objects.filter(date=day).select_related("patient", "doctor")
    doctors = User.objects.filter(role="doctor", is_active=True)
    doctor_id = request.GET.get("doctor", "")
    if request.user.role == "doctor":  # doctors see only their own schedule
        items = items.filter(doctor=request.user)
    elif doctor_id.isdigit():
        items = items.filter(doctor_id=int(doctor_id))
    return render(request, "appointments/list.html", {
        "items": items, "day": day, "prev": day - timedelta(days=1), "next": day + timedelta(days=1),
        "doctors": doctors, "doctor_id": doctor_id, "rights": STATUS_RIGHTS.get(request.user.role, set()),
        "is_today": day == date.today(),
    })


@role_required("receptionist")
def appointment_create(request):
    initial = {"patient": request.GET.get("patient"), "date": date.today()}
    form = AppointmentForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        appt = form.save(commit=False)
        appt.created_by = request.user
        appt.save()
        record(request, "create", f"Appointment #{appt.pk}", f"{appt.patient.mrn} on {appt.date} {appt.start_time:%H:%M}")
        messages.success(request, f"Booked {appt.patient.full_name} with {appt.doctor.get_full_name()} "
                                  f"at {appt.start_time:%H:%M}.")
        return redirect(f"/appointments/?date={appt.date.isoformat()}")
    return render(request, "appointments/form.html", {"form": form, "title": "Book appointment"})


@role_required("receptionist")
def appointment_edit(request, pk):
    appt = get_object_or_404(Appointment, pk=pk)
    if appt.status != "scheduled":
        messages.error(request, "Only scheduled appointments can be moved.")
        return redirect(f"/appointments/?date={appt.date.isoformat()}")
    form = AppointmentForm(request.POST or None, instance=appt)
    if request.method == "POST" and form.is_valid():
        form.save()
        record(request, "update", f"Appointment #{appt.pk}", "Rescheduled")
        messages.success(request, "Appointment updated.")
        return redirect(f"/appointments/?date={appt.date.isoformat()}")
    return render(request, "appointments/form.html", {"form": form, "title": "Reschedule appointment"})


@role_required("doctor", "receptionist")
@require_POST
def appointment_status(request, pk, new_status):
    appt = get_object_or_404(Appointment, pk=pk)
    if new_status not in STATUS_RIGHTS.get(request.user.role, set()):
        raise PermissionDenied
    if request.user.role == "doctor" and appt.doctor_id != request.user.id:
        raise PermissionDenied
    if appt.can_change_to(new_status):
        appt.status = new_status
        appt.save(update_fields=["status", "updated_at"])
        record(request, "status", f"Appointment #{appt.pk}", f"-> {appt.get_status_display()}")
        messages.success(request, f"{appt.patient.full_name}: {appt.get_status_display()}.")
    else:
        messages.error(request, f"This appointment is {appt.get_status_display().lower()} and cannot change.")
    return redirect(f"/appointments/?date={appt.date.isoformat()}")
