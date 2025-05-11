from django.contrib import admin
from audits.models import AuditLog
# Register your models here.

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "action", "action_type", "timestamp", "ip_address"]