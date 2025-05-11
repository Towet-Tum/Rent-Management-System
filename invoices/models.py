import uuid
from django.db import models
from lease.models import Lease
from property.models import TimestampedModel

# Create your models here.

class Invoice(TimestampedModel):
    class Status(models.TextChoices):
        ISSUED = 'issued', ('Issued')
        PAID = 'paid', ('Paid')
        OVERDUE = 'overdue', ('Overdue')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lease = models.ForeignKey(
        Lease,
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    period_start = models.DateField()
    period_end = models.DateField()
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ISSUED)

    class Meta:
        unique_together = ('lease', 'period_start', 'period_end')
        constraints = [
            models.CheckConstraint(
                check=models.Q(period_end__gte=models.F('period_start')),
                name='end_date_after_start'
            )
        ]
        indexes = [models.Index(fields=['lease', 'due_date']),]

    def __str__(self):
        return f"Invoice {self.id} - {self.lease.id}"
