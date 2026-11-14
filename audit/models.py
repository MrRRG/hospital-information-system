from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    """Append-only trail of who did what. Nobody edits or deletes rows from the web pages."""

    class Action(models.TextChoices):
        LOGIN = "login", "Signed in"
        LOGOUT = "logout", "Signed out"
        LOGIN_FAILED = "login_failed", "Failed sign-in"
        VIEW = "view", "Opened record"
        CREATE = "create", "Created"
        UPDATE = "update", "Changed"
        STATUS = "status", "Status change"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    username = models.CharField(max_length=150, blank=True)  # kept even if the user is removed later
    role = models.CharField(max_length=20, blank=True)
    action = models.CharField(max_length=14, choices=Action.choices)
    target = models.CharField(max_length=120, blank=True)
    details = models.CharField(max_length=250, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.timestamp:%Y-%m-%d %H:%M} {self.username} {self.action} {self.target}"
