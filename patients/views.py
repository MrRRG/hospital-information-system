from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from audit.utils import record

from .forms import MEDICAL_ROLES, PatientForm
from .models import Patient


@login_required
def patient_list(request):
    q = request.GET.get("q", "").strip()
    patients = Patient.objects.all()
    if q:
        patients = patients.filter(
            Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(mrn__icontains=q)
            | Q(national_id__icontains=q) | Q(phone__icontains=q)
        )
    page = Paginator(patients, 10).get_page(request.GET.get("page"))
    return render(request, "patients/list.html", {"page": page, "q": q})


@login_required
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    record(request, "view", f"Patient {patient.mrn}", patient.full_name)
    can_see = request.user.role in MEDICAL_ROLES
    visits = patient.visits.select_related("doctor")[:10] if can_see else []
    return render(request, "patients/detail.html", {
        "patient": patient, "can_see_medical": can_see, "visits": visits})


@login_required
def patient_create(request):
    form = PatientForm(request.POST or None, user=request.user)
    if request.method == "POST" and form.is_valid():
        patient = form.save(commit=False)
        patient.created_by = request.user
        patient.save()
        record(request, "create", f"Patient {patient.mrn}", patient.full_name)
        messages.success(request, f"Patient registered. File number: {patient.mrn}")
        return redirect("patient_detail", pk=patient.pk)
    return render(request, "patients/form.html", {"form": form, "title": "Register patient"})


@login_required
def patient_edit(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    form = PatientForm(request.POST or None, instance=patient, user=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        record(request, "update", f"Patient {patient.mrn}", "Fields: " + ", ".join(form.changed_data))
        messages.success(request, "Changes saved.")
        return redirect("patient_detail", pk=patient.pk)
    return render(request, "patients/form.html", {"form": form, "title": f"Edit {patient.full_name}"})
