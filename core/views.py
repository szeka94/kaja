from rest_framework import routers
from kaja.address.views import AddressViewSet


router = routers.DefaultRouter()

defined_viewsets = {"addresses": AddressViewSet}

for k, v in defined_viewsets.items():
    router.register(k, v)
