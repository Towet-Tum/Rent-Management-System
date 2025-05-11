import uuid
from django.db import models
from property.models import Unit, TimestampedModel
from django.conf import settings



class Lease(TimestampedModel):
    class Status(models.TextChoices):
        PENDING = 'pending', ('Pending')
        ACTIVE = 'active', ('Active')
        TERMINATED = 'terminated', ('Terminated')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        related_name='leases'
    )
    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='leases'
    )
    start_date = models.DateField()
    end_date = models.DateField()
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    class Meta:
        unique_together = ('unit', 'start_date')
        indexes = [models.Index(fields=['tenant', 'status']),]

    def __str__(self):
        return f"Lease {self.id} - {self.tenant.username}"