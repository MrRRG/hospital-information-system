from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class HISUserAdmin(UserAdmin):
    list_display = ("username", "get_full_name", "role", "is_active")
    list_filter = ("role", "is_active")
    fieldsets = UserAdmin.fieldsets + (("HIS role", {"fields": ("role",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("HIS role", {"fields": ("role",)}),)
