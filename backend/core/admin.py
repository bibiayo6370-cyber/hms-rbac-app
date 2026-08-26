from django.contrib import admin
from .models import Department, AuditLog


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "user", "action", "entity_type", "entity_id", "ip_address")
    list_filter = ("action", "entity_type")
    readonly_fields = [f.name for f in AuditLog._meta.fields]
    search_fields = ("entity_type", "entity_id", "description")

    def has_add_permission(self, request):
        return False  # audit logs are system-generated only

    def has_change_permission(self, request, obj=None):
        return False
