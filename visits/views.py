from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.permissions import role_required
from appointments.models import Appointment
from audit.utils import record
from patients.models import Patient

from .forms import VisitForm
from .models import Visit

STAFF = ("doctor", "nurse")  # administrators always pass role_required


@role_required(*STAFF)
def visit_list(request):
    q = request.GET.get("q", "").strip()
    visits = Visit.objects.select_related("patient", "doctor")
    if q:
        visits = visits.filter(Q(patient__first_name__icontains=q) | Q(patient__last_name__icontains=q)
                               | Q(patient__mrn__icontains=q) | Q(complaint__icontains=q))
    page = Paginator(visits, 15).get_page(request.GET.get("page"))
    return render(request, "visits/list.html", {"page": page, "q": q})


@role_required(*STAFF)
def visit_create(request):
    appointment = None
    if request.GET.get("appointment", "").isdigit():
        appointment = get_object_or_404(Appointment, pk=int(request.GET["appointment"]))
        patient = appointment.patient
    else:
        patient = get_object_or_404(Patient, pk=request.GET.get("patient") or 0)
    initial = {"complaint": appointment.reason} if appointment else {}
    form = VisitForm(request.POST or None, initial=initial, user=request.user)
    if request.method == "POST" and form.is_valid():
        visit = form.save(commit=False)
        visit.patient, visit.created_by = patient, request.user
        if request.user.role == "doctor":
            visit.doctor = request.user
        elif appointment:
            visit.doctor = appointment.doctor
        if appointment and not hasattr(appointment, "visit"):
            visit.appointment = appointment
        visit.save()
        # Seeing the patient finishes a checked-in appointment.
        if visit.appointment and request.user.role == "doctor" and visit.appointment.status == "checked_in":
            visit.appointment.status = "completed"
            visit.appointment.save(update_fields=["status", "updated_at"])
        record(request, "create", f"Visit #{visit.pk}", f"Patient {patient.mrn}")
        messages.success(request, "Visit saved.")
        return redirect("visit_detail", pk=visit.pk)
    return render(request, "visits/form.html", {"form": form, "patient": patient, "title": "New visit"})


@role_required(*STAFF)
def visit_detail(request, pk):
    visit = get_object_or_404(Visit.objects.select_related("patient", "doctor"), pk=pk)
    record(request, "view", f"Visit #{visit.pk}", f"Patient {visit.patient.mrn}")
    return render(request, "visits/detail.html", {"visit": visit})


@role_required(*STAFF)
def visit_edit(request, pk):
    visit = get_object_or_404(Visit, pk=pk)
    form = VisitForm(request.POST or None, instance=visit, user=request.user)
    if request.method == "POST" and form.is_valid():
        visit = form.save(commit=False)
        if request.user.role == "doctor" and visit.doctor_id is None:
            visit.doctor = request.user
        visit.save()
        record(request, "update", f"Visit #{visit.pk}", f"Patient {visit.patient.mrn}")
        messages.success(request, "Changes saved.")
        return redirect("visit_detail", pk=visit.pk)
    return render(request, "visits/form.html", {"form": form, "patient": visit.patient, "title": "Edit visit"})
