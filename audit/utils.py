from .models import AuditLog


def record(request, action, target="", details=""):
    """Write one audit row. Call it from any view that touches patient data."""
    user = request.user if request.user.is_authenticated else None
    AuditLog.objects.create(
        user=user, username=getattr(user, "username", ""), role=getattr(user, "role", ""),
        action=action, target=str(target)[:120], details=str(details)[:250],
        ip_address=request.META.get("REMOTE_ADDR") or None,
    )
