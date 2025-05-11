import uuid
from django.db import models
from django.conf import settings

# Create your models here.
class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Property(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    landlord = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='properties'
    )
    name = models.CharField(max_length=100)
    address_line1 = models.CharField(max_length=150)
    address_line2 = models.CharField(max_length=150, blank=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=50)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=['landlord']),]
        verbose_name_plural = 'properties'

    def __str__(self):
        return f"{self.name} ({self.city})"


# models.py
class Amenity(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.ImageField(upload_to='amenity_icons/', null=True, blank=True)  # optional
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Unit(models.Model):
    class UnitType(models.TextChoices):
        SINGLE = 'single', ('Single')
        BEDSITTER = 'bedsitter', ('Bedsitter')
        SELF_CONTAINED = 'self_contained', ('Self Contained')
        ONE_BEDROOM = 'one_bedroom', ('One Bedroom')
        TWO_BEDROOM = 'two_bedroom', ('Two Bedroom')
        OTHER = 'other', ('Other')
        
    class Status(models.TextChoices):
        AVAILABLE = 'available', ('Available')
        OCCUPIED = 'occupied', ('Occupied')
        MAINTENANCE = 'maintenance', ('Maintenance')

    property = models.ForeignKey('Property', on_delete=models.CASCADE, related_name='units')
    amenities = models.ManyToManyField(Amenity, blank=True, related_name='units')
    unit_number = models.CharField(max_length=20)  # e.g. A1, B12
    unit_type = models.CharField(max_length=30, choices=UnitType.choices, default=UnitType.SINGLE)
  
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        unique_together = ('property', 'unit_number')
        indexes = [models.Index(fields=['property', 'status']),]

    def __str__(self):
        return f"{self.unit_number} ({self.get_unit_type_display()}) - {self.property.name}"
    
class RentAdjustment(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='adjustments')
    new_rent = models.DecimalField(max_digits=10, decimal_places=2)
    effective_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['effective_date']
        # ensure you don’t schedule two adjustments for the same date:
        unique_together = ('unit', 'effective_date')

    
    


class UnitGallery(models.Model):
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, related_name='gallery')
    image = models.ImageField(upload_to='unit_images/')
    caption = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.unit.unit_number} - {self.caption or 'No caption'}"

