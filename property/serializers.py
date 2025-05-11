from rest_framework import serializers
from property.models import Property, Unit, Amenity, UnitGallery, RentAdjustment


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = '__all__'
        
class UnitSerializer(serializers.ModelSerializer):
    amenities = serializers.PrimaryKeyRelatedField(many=True, queryset=Amenity.objects.all())

    class Meta:
        model = Unit
        fields = "__all__"


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ['id', 'name', 'icon', 'description'] 
    
class RentAdjustmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RentAdjustment
        fields = ['id', 'unit', 'new_rent', 'effective_date', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_unit(self, unit):
        # Ensure only the unit’s landlord can schedule its adjustment
        request = self.context['request']
        if unit.property.landlord != request.user:
            raise serializers.ValidationError("You can only adjust your own units.")
        return unit

class UnitGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitGallery
        fields = ['id', 'unit', 'image', 'caption', 'uploaded_at']