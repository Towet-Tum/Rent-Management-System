from django.contrib import admin
from .models import Invoice
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'lease', 'period_start', 'period_end', 'amount_due', 'due_date', 'status')
    list_filter = ('status', 'due_date', 'lease')
    search_fields = ('id', 'lease__id')
    ordering = ('-due_date',)
    date_hierarchy = 'due_date'
