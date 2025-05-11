from django.db import transaction, models as dj_models
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters
from audits.models import AuditLog
# Create your models here.

# Create your views here.
# Centralized mixin for audit logging
class AuditMixin:
    def perform_action(self, action_desc, user=None, **kwargs):
        AuditLog.objects.create(
            user=user or self.request.user,
            action=action_desc,
            ip_address=self.request.META.get('REMOTE_ADDR', '')
        )

class BaseViewSet(viewsets.ModelViewSet, AuditMixin):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = '__all__'
    search_fields = ['id']
    ordering_fields = ['id']

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        self.perform_action(f"Created {self.basename}: {response.data.get('id')}")
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        self.perform_action(f"Updated {self.basename}: {response.data.get('id')}")
        return response

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        obj_id = getattr(instance, 'id', '')
        response = super().destroy(request, *args, **kwargs)
        self.perform_action(f"Deleted {self.basename}: {obj_id}")
        return response