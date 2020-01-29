from core.test_base import TestBase
from kaja.address.models import Address


class TestAddressModel(TestBase):
    def test_saves_formatted_address(self):
        address = Address.objects.create(
            city="Kezdivasarhely",
            street="Kozpont",
            address="10es szam",
            zip_code="525400",
            region="CV",
            country="Romania",
        )
        self.assertEqual(address.formated_address, "Kozpont/10es szam, Kezdivasarhely CV 525400")
