# property/tasks.py

from celery import shared_task
from django.utils import timezone
from django.db import transaction
from property.models import RentAdjustment

@shared_task
def apply_advance_rent_adjustments():
    """
    Apply all RentAdjustment entries whose effective_date is today or earlier.
    Bulk-update the related Unit.rent_amount and then delete those adjustments.
    """
    today = timezone.now().date()
    # Grab all due adjustments
    adjustments = (RentAdjustment.objects
                   .filter(effective_date__lte=today)
                   .select_related('unit'))
    if not adjustments:
        return 'No rent adjustments due today.'

    # Prepare for bulk update
    units_to_update = []
    adj_ids = []
    for adj in adjustments:
        unit = adj.unit
        unit.rent_amount = adj.new_rent
        units_to_update.append(unit)
        adj_ids.append(adj.id)

    with transaction.atomic():
        # Update rent_amount on all affected units
        from property.models import Unit
        Unit.objects.bulk_update(units_to_update, ['rent_amount'])
        # Remove the adjustments we've just applied
        RentAdjustment.objects.filter(id__in=adj_ids).delete()

    return f'Applied {len(adj_ids)} rent adjustments.'
