from rest_framework.permissions import BasePermission
from .models import User


class IsAdmin(BasePermission):
    """
    Allows access only to users with role 'admin'.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == User.Role.ADMIN)


class IsLandlord(BasePermission):
    """
    Allows access only to users with role 'landlord'.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == User.Role.LANDLORD)

    def has_object_permission(self, request, view, obj):
        # Landlord can only interact with their own objects
        # Assumes the model has a 'landlord' FK or property
        landlord = getattr(obj, 'landlord', None) or getattr(obj, 'property', None) and getattr(obj.property, 'landlord', None)
        return bool(request.user.role == User.Role.LANDLORD and landlord == request.user)
    
    
class IsLandlordOrAdmin(BasePermission):
    """
    Allows access to landlords on their own objects or any admin.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role in [User.Role.LANDLORD, User.Role.ADMIN])

    def has_object_permission(self, request, view, obj):
        if request.user.role == User.Role.ADMIN:
            return True
        # Landlord: same as IsLandlord.object permission
        landlord = getattr(obj, 'landlord', None) or getattr(obj, 'property', None) and getattr(obj.property, 'landlord', None)
        return landlord == request.user



class IsTenant(BasePermission):
    """
    Allows access only to users with role 'tenant'.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == User.Role.TENANT)

    def has_object_permission(self, request, view, obj):
        # Tenant can only interact with their own objects
        # Handles Lease, Invoice, Payment via 'tenant' or 'invoice.lease.tenant'
        if hasattr(obj, 'tenant'):
            return obj.tenant == request.user
        if hasattr(obj, 'lease') and hasattr(obj.lease, 'tenant'):
            return obj.lease.tenant == request.user
        return False




class IsTenantOrAdmin(BasePermission):
    """
    Allows access to tenants on their own objects or any admin.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role in [User.Role.TENANT, User.Role.ADMIN])

    def has_object_permission(self, request, view, obj):
        if request.user.role == User.Role.ADMIN:
            return True
        if hasattr(obj, 'tenant'):
            return obj.tenant == request.user
        if hasattr(obj, 'lease') and hasattr(obj.lease, 'tenant'):
            return obj.lease.tenant == request.user
        return False


class RolePermission(BasePermission):
    """
    Generic permission that checks for one or more allowed roles.
    Usage: permission_classes = [RolePermission(allowed_roles=['admin', 'landlord'])]
    """
    def __init__(self, allowed_roles=None):
        self.allowed_roles = allowed_roles or []

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role in self.allowed_roles)

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
