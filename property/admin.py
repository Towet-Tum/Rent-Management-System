from django.contrib import admin
from .models import Property, Amenity, Unit, UnitGallery, RentAdjustment

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'state', 'country', 'landlord', 'created_at', 'updated_at')
    search_fields = ('name', 'city', 'state', 'country', 'landlord__username')
    list_filter = ('city', 'state', 'country', 'created_at')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('unit_number', 'property', 'unit_type', 'rent_amount', 'status', 'created_at', 'updated_at')
    search_fields = ('unit_number', 'property__name', 'unit_type')
    list_filter = ('unit_type', 'status', 'created_at')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(UnitGallery)
class UnitGalleryAdmin(admin.ModelAdmin):
    list_display = ('unit', 'caption', 'uploaded_at')
    search_fields = ('unit__unit_number', 'caption')
    list_filter = ('uploaded_at',)
    ordering = ('-uploaded_at',)
    readonly_fields = ('uploaded_at',)
    
    @admin.register(RentAdjustment)
    class RentAdjustmentAdmin(admin.ModelAdmin):
        list_display = ('unit', 'new_rent', 'effective_date', 'created_at')
        search_fields = ('unit__unit_number',)
        list_filter = ('effective_date', 'created_at')
        ordering = ('-effective_date',)
        readonly_fields = ('created_at',)