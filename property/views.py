from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from accounts.permissions import IsAdmin, IsLandlord, IsTenant
from property.models import Property, Unit, Amenity, RentAdjustment
from accounts.models import User  # Import the User model
from property.serializers import PropertySerializer, UnitSerializer, AmenitySerializer, RentAdjustmentSerializer
from audits.views import BaseViewSet
from rest_framework.decorators import action
from rest_framework.response import Response


class PropertyViewSet(BaseViewSet):
    queryset = Property.objects.select_related('user')
    serializer_class = PropertySerializer
    search_fields = ['user__username', 'phone']
    
    def get_permissions(self):
        """Customize permission logic for each action."""
        if self.action == 'list_property':
            return [AllowAny()]
        elif self.action in ['create_property', 'update_property', 'delete_property', 'me']:
            return [IsAuthenticated(), IsLandlord()]
        return [IsAuthenticated()]
    


    def get_queryset(self):
        """Filter queryset based on role."""
        user = self.request.user
        if user.role == User.Role.LANDLORD:
            return Property.objects.filter(landlord=user)
        return super().get_queryset()

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        """Return the current logged-in properties."""
        properties = Property.objects.filter(landlord=request.user)

        if properties:
            serializer = self.get_serializer(properties, many=True)
            return Response(serializer.data)
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], url_path='list')
    def list_property(self, request):
        """List all parents (Landlord only)."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['put'], url_path='update')
    def update_property(self, request, pk=None):
        """Update property_instance details (Landlord only)."""
        property_instance = self.get_object()
        serializer = self.get_serializer(property_instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='delete')
    def delete_property(self, request, pk=None):
        """Delete a property_instance (Landlord only)."""
        property_instance = self.get_object()
        property_instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], url_path='create')
    def create_property(self, request):
        """Create a new property_instance (Landlord only)."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AmenityViewSet(viewsets.ModelViewSet):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    
class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.select_related('property')
    serializer_class = UnitSerializer
    search_fields = ['user__username', 'phone']
    
    def get_permissions(self):
        """Customize permission logic for each action."""
        if self.action == 'list_unit':
            return [AllowAny()]
        elif self.action in ['unit_create', 'update_unit', 'delete_unit', 'me']:
            return [IsAuthenticated(), IsLandlord()]
        return [IsAuthenticated()]
    


    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.LANDLORD:
            # follow the FK from Unit → Property → landlord
            return Unit.objects.filter(property__landlord=user)
        
        return super().get_queryset()


    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        """Return the current logged-in properties."""
        units = Unit.objects.filter(property__landlord=request.user)

        if units:
            serializer = self.get_serializer(units, many=True)
            return Response(serializer.data)
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], url_path='list')
    def list_unit(self, request):
        """List all parents (anyone)."""
        queryset = Unit.objects.all()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['put'], url_path='update')
    def update_unit(self, request, pk=None):
        """Update property_instance details (Landlord only)."""
        unit_instance = self.get_object()
        serializer = self.get_serializer(unit_instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='delete')
    def delete_unit(self, request, pk=None):
        """Delete a unit_instance (Landlord only)."""
        unit_instance = self.get_object()
        unit_instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], url_path='create')
    def unit_create(self, request):
        """Create a new property_instance (Landlord only)."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class RentAdjustmentViewSet(viewsets.ModelViewSet):
    """
    Allows landlords to schedule rent changes by creating RentAdjustment entries.
    """
    queryset = RentAdjustment.objects.select_related('unit', 'unit__property')
    serializer_class = RentAdjustmentSerializer
    permission_classes = [IsAuthenticated, IsLandlord]

    def get_queryset(self):
        # Only show adjustments for units the landlord owns
        user = self.request.user
        return self.queryset.filter(unit__property__landlord=user)
   
