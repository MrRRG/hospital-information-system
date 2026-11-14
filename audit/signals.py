from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver

from .models import AuditLog


def _ip(request):
    return request.META.get("REMOTE_ADDR") if request is not None else None


@receiver(user_logged_in)
def on_login(sender, request, user, **kwargs):
    AuditLog.objects.create(user=user, username=user.username, role=user.role,
                            action="login", ip_address=_ip(request))


@receiver(user_logged_out)
def on_logout(sender, request, user, **kwargs):
    if user is not None:
        AuditLog.objects.create(user=user, username=user.username, role=user.role,
                                action="logout", ip_address=_ip(request))


@receiver(user_login_failed)
def on_failed(sender, credentials, request=None, **kwargs):
    AuditLog.objects.create(username=str(credentials.get("username", ""))[:150],
                            action="login_failed", ip_address=_ip(request))
