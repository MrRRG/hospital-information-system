from django.core.paginator import Paginator
from django.shortcuts import render

from accounts.permissions import role_required

from .models import AuditLog


@role_required()  # administrators only
def audit_list(request):
    logs = AuditLog.objects.all()
    q = request.GET.get("q", "").strip()
    action = request.GET.get("action", "")
    if q:
        logs = logs.filter(username__icontains=q) | logs.filter(target__icontains=q)
    if action:
        logs = logs.filter(action=action)
    page = Paginator(logs, 25).get_page(request.GET.get("page"))
    return render(request, "audit/list.html", {"page": page, "q": q, "action": action,
                                               "actions": AuditLog.Action.choices})
