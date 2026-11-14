from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """HIS user. The role decides which modules the person can open."""

    class Role(models.TextChoices):
        ADMIN = "admin", _("Administrator")
        DOCTOR = "doctor", _("Doctor")
        NURSE = "nurse", _("Nurse")
        RECEPTIONIST = "receptionist", _("Receptionist")

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.RECEPTIONIST)

    def save(self, *args, **kwargs):
        # Superusers created from the command line are always administrators.
        if self.is_superuser:
            self.role = self.Role.ADMIN
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
