from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class HIMSUserAdmin(UserAdmin):
    list_display = ("username", "get_full_name", "role", "department", "is_active_staff", "is_active")
    list_filter = ("role", "department", "is_active", "is_active_staff")
    fieldsets = UserAdmin.fieldsets + (
        ("HIMS role & staff info", {"fields": ("role", "phone_number", "department", "is_active_staff")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("HIMS role & staff info", {"fields": ("role", "phone_number", "department", "is_active_staff")}),
    )
