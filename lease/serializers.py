from rest_framework import serializers
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from .models import Lease
from property.models import Unit
from invoices.models import Invoice

class LeaseSerializer(serializers.ModelSerializer):
    unit = serializers.PrimaryKeyRelatedField(queryset=Unit.objects.all())
    unit_detail = serializers.SerializerMethodField(read_only=True)
    tenant = serializers.HiddenField(default=serializers.CurrentUserDefault())
    
    # Make rent_amount and deposit_amount optional
    rent_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    deposit_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

    class Meta:
        model = Lease
        fields = [
            'id', 'unit', 'unit_detail', 'tenant',
            'start_date', 'end_date', 'rent_amount', 'deposit_amount', 'status',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'unit_detail', 'created_at', 'updated_at', 'status']

    def get_unit_detail(self, obj):
        return {
            'id': str(obj.unit.id),
            'unit_number': obj.unit.unit_number,
            'unit_type': obj.unit.get_unit_type_display(),
            'property': {
                'id': str(obj.unit.property.id),
                'name': obj.unit.property.name,
                'city': obj.unit.property.city,
            }
        }

    def validate(self, data):
        start = data.get('start_date', getattr(self.instance, 'start_date', None))
        end = data.get('end_date', getattr(self.instance, 'end_date', None))
        unit = data.get('unit', getattr(self.instance, 'unit', None))

        if start and end and end < start:
            raise serializers.ValidationError({'end_date': 'End date must be on or after start date.'})

        qs = Lease.objects.filter(unit=unit)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        if qs.filter(start_date__lte=end, end_date__gte=start).exists():
            raise serializers.ValidationError('This unit is already leased during the requested period.')

        return data

    def create(self, validated_data):
        unit = validated_data['unit']
        if 'rent_amount' not in validated_data:
            validated_data['rent_amount'] = unit.rent_amount
        lease = super().create(validated_data)
        self._generate_invoices(lease)
        return lease

    def update(self, instance, validated_data):
        validated_data.pop('tenant', None)
        validated_data.pop('unit', None)
        return super().update(instance, validated_data)

    def _generate_invoices(self, lease):
        """
        Generate monthly invoices from lease.start_date to lease.end_date.
        """
        start = lease.start_date
        end = lease.end_date
        period_start = start
        invoices = []
        while period_start <= end:
            next_start = (period_start + relativedelta(months=1))
            period_end = min(end, next_start - timezone.timedelta(days=1))
            due_date = period_start + relativedelta(days=lease.lease_term_days if hasattr(lease, 'lease_term_days') else 30)
            invoices.append(Invoice(
                lease=lease,
                period_start=period_start,
                period_end=period_end,
                amount_due=lease.rent_amount,
                due_date=due_date
            ))
            period_start = next_start
        # Bulk create invoices
        Invoice.objects.bulk_create(invoices)
