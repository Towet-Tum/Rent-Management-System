from rest_framework import serializers
from django.utils import timezone
from .models import Invoice
from lease.models import Lease
from property.models import Unit

class InvoiceSerializer(serializers.ModelSerializer):
    # Write: accept lease by PK; Read: include nested lease info
    lease = serializers.PrimaryKeyRelatedField(queryset=Lease.objects.all())
    lease_detail = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'lease', 'lease_detail',
            'period_start', 'period_end', 'amount_due', 'due_date', 'status',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'lease_detail', 'created_at', 'updated_at', 'status']

    def get_lease_detail(self, obj):
        unit = obj.lease.unit
        return {
            'id': str(obj.lease.id),
            'unit_number': unit.unit_number,
            'property': {
                'id': str(unit.property.id),
                'name': unit.property.name,
                'city': unit.property.city,
            },
            'tenant': str(obj.lease.tenant.id),
            'start_date': obj.lease.start_date,
            'end_date': obj.lease.end_date,
        }

    def validate(self, data):
        # Ensure period_end >= period_start and due_date >= period_start
        start = data.get('period_start', getattr(self.instance, 'period_start', None))
        end = data.get('period_end', getattr(self.instance, 'period_end', None))
        due = data.get('due_date', getattr(self.instance, 'due_date', None))
        if start and end and end < start:
            raise serializers.ValidationError({'period_end': 'Period end must be on or after period start.'})
        if start and due and due < start:
            raise serializers.ValidationError({'due_date': 'Due date must be on or after period start.'})
        # Unique constraint overlap
        qs = Invoice.objects.filter(
            lease=data.get('lease', getattr(self.instance, 'lease', None)),
            period_start=data.get('period_start', getattr(self.instance, 'period_start', None)),
            period_end=data.get('period_end', getattr(self.instance, 'period_end', None)),
        )
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError('An invoice for this lease and period already exists.')
        return data

    def create(self, validated_data):
        # Default amount_due to lease rent if omitted
        lease = validated_data['lease']
        if 'amount_due' not in validated_data or validated_data['amount_due'] is None:
            validated_data['amount_due'] = lease.rent_amount
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Prevent changing lease or period once created
        validated_data.pop('lease', None)
        validated_data.pop('period_start', None)
        validated_data.pop('period_end', None)
        return super().update(instance, validated_data)
