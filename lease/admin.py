from django.contrib import admin
from .models import Lease
@admin.register(Lease)
class LeaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'unit', 'tenant', 'start_date', 'end_date', 'rent_amount', 'deposit_amount', 'status')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('tenant__username', 'unit__name', 'id')
    ordering = ('-start_date',)
    readonly_fields = ('id',)
# Register your models here.
