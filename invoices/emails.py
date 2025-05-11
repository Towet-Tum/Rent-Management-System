from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

# TODO:
# Design the HTML templates for the emails in the frontend (e.g., templates/emails/invoice_reminder.html)

def send_overdue_notification(invoice, template):
    tenant = invoice.lease.tenant
    context = {
        'invoice': invoice,
        'tenant': tenant,
    }
    html_content = render_to_string(template, context)
    plain_message = strip_tags(html_content)
    subject = f"Overdue Invoice Reminder: Invoice #{invoice.id}"
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[tenant.email],
        html_message=html_content,
    )

def send_invoice_reminder(invoice, template):
    tenant = invoice.lease.tenant
    context = {'invoice': invoice, 'tenant': tenant}
    html_content = render_to_string(template, context)
    plain_message = strip_tags(html_content)
    subject = f"Reminder: Invoice due on {invoice.due_date}"

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[tenant.email],
        html_message=html_content,
    )
