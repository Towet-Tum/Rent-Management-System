# property/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import Lease
from .serializers import LeaseSerializer
from invoices.models import Invoice
from accounts.permissions import IsLandlord, IsTenant
from invoices.tasks import dispatch_due_reminders

def is_landlord_of_lease(self, lease, user):
    return user.role == user.Role.LANDLORD and lease.unit.property.landlord == user

class LeaseViewSet(viewsets.ModelViewSet):
    queryset = Lease.objects.select_related('unit__property', 'tenant')
    serializer_class = LeaseSerializer
   

    def get_permissions(self):
        if self.action in ['lease_create','update_lease','delete_lease','terminate']:
            return [IsAuthenticated(), IsLandlord()]
        if self.action in ['me','invoices','retrieve','list']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsTenant()]


    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'role', None) == user.Role.LANDLORD:
            return self.queryset.filter(unit__property__landlord=user)
        return self.queryset.filter(tenant=user)

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        """Return leases for the current user (tenant or landlord)."""
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='list')
    def list_lease(self, request):
        """List all leases (tenant sees own, landlord sees own)."""
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['put'], url_path='update')
    def update_lease(self, request, pk=None):
        """Update a lease (Landlord only)."""
        lease = self.get_object()
        serializer = self.get_serializer(lease, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='delete')
    def delete_lease(self, request, pk=None):
        """Delete a lease (Landlord only)."""
        lease = self.get_object()
        lease.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], url_path='create')
    def lease_create(self, request):
        """Create a new lease (Landlord only)."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            lease = serializer.save(status=Lease.Status.PENDING)
            return Response(self.get_serializer(lease).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='activate')
    def activate(self, request, pk=None):
        """Activate a pending lease: status -> ACTIVE."""
        lease = self.get_object()
        if lease.status != Lease.Status.PENDING:
            return Response({'detail': 'Only pending leases can be activated.'}, status=status.HTTP_400_BAD_REQUEST)
        lease.status = Lease.Status.ACTIVE
        lease.save(update_fields=['status'])
        for inv in lease.invoices.all():
            dispatch_due_reminders.delay()
        return Response(self.get_serializer(lease).data)

    @action(detail=True, methods=['post'], url_path='terminate')
    def terminate(self, request, pk=None):
        """Terminate an active lease: status -> TERMINATED and clean future invoices."""
        lease = self.get_object()
        if lease.status != Lease.Status.ACTIVE:
            return Response({'detail': 'Only active leases can be terminated.'}, status=status.HTTP_400_BAD_REQUEST)
        lease.status = Lease.Status.TERMINATED
        lease.end_date = timezone.now().date()
        lease.save(update_fields=['status', 'end_date'])
        Invoice.objects.filter(lease=lease, period_start__gt=lease.end_date).delete()
        return Response(self.get_serializer(lease).data)

    @action(detail=True, methods=['get'], url_path='invoices')
    def invoices(self, request, pk=None):
        """List all invoices for a given lease."""
        lease = self.get_object()
        inv_qs = Invoice.objects.filter(lease=lease).order_by('period_start')
        data = [{
            'id': str(inv.id),
            'period_start': inv.period_start,
            'period_end': inv.period_end,
            'amount_due': inv.amount_due,
            'due_date': inv.due_date,
            'status': inv.status
        } for inv in inv_qs]
        return Response(data)
