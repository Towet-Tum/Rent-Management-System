import uuid
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


# Custom User model
class User(AbstractUser):
    class Role(models.TextChoices):
        LANDLORD = 'landlord', _('Landlord')
        TENANT = 'tenant', _('Tenant')
        ADMIN = 'admin', _('Admin')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.TENANT)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
