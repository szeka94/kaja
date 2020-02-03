from django.core.validators import ValidationError

from core.test_base import TestBase
from kaja.restaurant.models import Restaurant
from kaja.user.models import UserProfile
from kaja.address.models import Address


class TestAddressModel(TestBase):
    def setUp(self):
        super(TestAddressModel, self).setUp()
        self.profile = self.make(UserProfile)
        self.restaurant = self.make(Restaurant)

    def test_saves_formatted_address(self):
        address = Address.objects.create(
            city="kezdivasarhely",
            street="Kozpont",
            address="10es szam",
            zip_code="525400",
            region="cv",
            country="romania",
        )
        self.assertEqual(address.formated_address, "Kozpont/10es szam, kezdivasarhely cv 525400")

    def test_address_cannot_have_restaurant_and_profile_prop_in_the_same_time(self):
        address = self.make(Address)
        address.profile = self.profile
        address.restaurant = self.restaurant
        with self.assertRaises(ValidationError):
            address.save()

    # def test_only_supported_city_region_country_is_allowed(self):
    #     address = self.make(Address)
    #     for attr_name, attr_value in [
    #         ("city", "Szentgyorgy"),
    #         ("region", "CJ"),
    #         ("country", "Hungary"),
    #     ]:
    #         setattr(address, attr_name, attr_value)
    #         address.save()
    #         breakpoint()
