from django.db.models import Q
from rest_framework import status, viewsets

from kaja.address.models import Address
from kaja.address.serializers import AddressSerializer


class AddressViewSet(viewsets.ModelViewSet):
    """
    Provides access to restaurant/user addresses
    """

    queryset = Address.objects.all()
    serializer_class = AddressSerializer

    def get_queryset(self):
        """
            TODO: be very-very sure that no user-address can be created with a restaurant
                  relationship
        """
        qs = super(AddressViewSet, self).get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(Q(profile=self.request.user.profile) | Q(restaurant__isnull=False))
        return qs

    def get_serializer_context(self):
        return {"user": self.request.user}
