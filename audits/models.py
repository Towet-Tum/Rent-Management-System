from django.db import models
from django.conf import settings

# ---------------------------
# System and Logs
# ---------------------------
class AuditLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.TextField()
    action_type = models.CharField(max_length=20, choices=[('Create', 'Create'), ('Update', 'Update'), ('Delete', 'Delete')])
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()

    def __str__(self):
        return f"{self.user} - {self.action_type}"
    
