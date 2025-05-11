# invoices/tasks.py
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from .models import Invoice
from .emails import send_invoice_reminder, send_overdue_notification
from django.db import transaction

@shared_task
def dispatch_due_reminders():
    today = timezone.now().date()
    for cfg in settings.REMINDER_SCHEDULE:
        target = today + timezone.timedelta(days=cfg['days_before'])
        qs = Invoice.objects.filter(
            due_date=target,
            status=Invoice.Status.ISSUED
        ).select_related('lease__tenant')
        for inv in qs:
            send_invoice_reminder(inv, template=cfg['template'])


@shared_task
def mark_overdue_invoices():
    """
    Find all invoices where due_date < today and status is ISSUED,
    set their status to OVERDUE in bulk.
    """
    today = timezone.now().date()

    # Select invoices due before today and still ISSUED
    overdue_qs = Invoice.objects.filter(
        due_date__lt=today,
        status=Invoice.Status.ISSUED
    )

    count = overdue_qs.count()
    if count == 0:
        return f'No invoices to mark overdue on {today}.'

    # Bulk update for efficiency
    with transaction.atomic():
        overdue_qs.update(status=Invoice.Status.OVERDUE)

    return f'Marked {count} invoices as OVERDUE.'

@shared_task
def mark_and_notify_overdue():
    today = timezone.now().date()
    with transaction.atomic():
        overdue_qs = Invoice.objects.filter(
            due_date__lt=today,
            status=Invoice.Status.ISSUED
        )
        count = overdue_qs.count()
        for inv in overdue_qs:
            inv.status = Invoice.Status.OVERDUE
            inv.save(update_fields=['status'])
            send_overdue_notification(inv)
    return f'Processed {count} overdue invoices.'