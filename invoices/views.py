# invoices/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Invoice
from .serializers import InvoiceSerializer
from lease.models import Lease
from accounts.permissions import IsTenant, IsLandlord

class InvoiceViewSet(viewsets.ModelViewSet):
    """
    CRUD for Invoices:
    - Landlords: can list/retrieve invoices for their leases, mark as issued/overdue.
    - Tenants: can list/retrieve/pay their own invoices.
    - Admins: full access.
    """
    queryset = Invoice.objects.select_related('lease__unit', 'lease__tenant')
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        # Creation is internal (e.g. by a scheduler), not via API:
        if self.action in ['create', 'destroy']:
            return [IsAuthenticated(), IsLandlord()]
        # Paying is tenant or admin:
        if self.action in ['pay', 'list_my', 'list']:
            return [IsAuthenticated(), IsTenant()]
        # Marking overdue or other admin actions:
        return [IsAuthenticated(), IsLandlord()]

    def get_queryset(self):
        user = self.request.user
        if user.role == user.Role.LANDLORD:
            # All invoices for leases on this landlord's units
            return self.queryset.filter(lease__unit__property__landlord=user)
        if user.role == user.Role.TENANT:
            # Only this tenant's invoices
            return self.queryset.filter(lease__tenant=user)
        # Admin sees all
        return self.queryset

    def perform_create(self, serializer):
        """
        Not exposed publicly; creation happens via leasing logic or a scheduled job.
        Ensures invoice.amount_due matches the lease rent_amount.
        """
        lease = serializer.validated_data['lease']
        if serializer.validated_data['amount_due'] is None:
            serializer.validated_data['amount_due'] = lease.rent_amount
        serializer.save()

    @action(detail=True, methods=['post'], url_path='pay')
    def pay(self, request, pk=None):
        """
        Mark an issued/overdue invoice as paid.
        """
        invoice = self.get_object()

        if invoice.status == Invoice.Status.PAID:
            return Response({'detail': 'Invoice already paid.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Here you'd integrate payment logic; for now, just set status:
        invoice.status = Invoice.Status.PAID
        invoice.save(update_fields=['status'])

        return Response(self.get_serializer(invoice).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='mine')
    def list_my(self, request):
        """
        Shortcut for tenants to list their invoices.
        """
        qs = self.get_queryset()
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='mark-overdue')
    def mark_overdue(self, request, pk=None):
        """
        Landlord/admin can manually mark an invoice as overdue.
        """
        invoice = self.get_object()
        if invoice.status != Invoice.Status.ISSUED:
            return Response({'detail': 'Only issued invoices can be marked overdue.'},
                            status=status.HTTP_400_BAD_REQUEST)

        invoice.status = Invoice.Status.OVERDUE
        invoice.save(update_fields=['status'])
        return Response(self.get_serializer(invoice).data, status=status.HTTP_200_OK)
