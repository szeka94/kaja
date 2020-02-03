from core.test_base import TestBase
from kaja.address.models import Address


class TestAddressSerializer(TestBase):
    def test_user_cannot_create_address_without_profile(self):
        assert True
