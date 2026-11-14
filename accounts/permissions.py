from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(*roles):
    """Allow a view only for the listed roles (admins always pass)."""

    def decorator(view):
        @wraps(view)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.role == "admin" or request.user.role in roles:
                return view(request, *args, **kwargs)
            raise PermissionDenied

        return wrapper

    return decorator
