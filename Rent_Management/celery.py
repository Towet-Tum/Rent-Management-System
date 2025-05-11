import os
from celery import Celery
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Rent_Management.settings')

app = Celery('Rent_Management')

# read config from Django settings, the CELERY_ namespace will be used:
app.config_from_object('django.conf:settings', namespace='CELERY')

# discover and load all task modules from all registered Django app configs.
app.autodiscover_tasks()

# Use the built-in beat scheduler that respects beat_schedule in code
app.conf.beat_scheduler = 'celery.beat.PersistentScheduler'

# Define your periodic tasks here:
app.conf.beat_schedule = {
    'apply-advance-rent-adjustments-daily': {
        'task': 'property.tasks.apply_advance_rent_adjustments',
        # run every day at 09:11
        'schedule': crontab(hour=9, minute=44),
        # no custom queue; uses default 'celery' queue
    },
    
    'send-invoice-reminders-every-day': {
    'task': 'invoices.tasks.dispatch_due_reminders',
        'schedule': crontab(hour=8, minute=0),
        },
    
    
    'mark-overdue-invoices-every-morning': {
        'task': 'invoices.tasks.mark_overdue_invoices',
        'schedule': crontab(hour=0, minute=5),
    },
}

