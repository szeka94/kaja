from django.db.utils import IntegrityError

from kaja.restaurant.models import Restaurant, Address, Chain
from core.test_base import TestBase


class TestRestaurantModel(TestBase):
    def setUp(self):
        super(TestRestaurantModel, self).setUp()
        self.address = Address.objects.create(
            city="Kezdivasarhely",
            street="Stadion",
            address="nr. 7, ap. 3",
            zip_code="525400",
            region="CV",
            country="Romania",
        )

    def test_restaurant_creates_default_chain(self):
        restaurant = Restaurant.objects.create(
            address=self.address, name="Jazz Cafe", contact=self.restaurant_contact
        )
        self.assertEqual(restaurant.chain.name, "Jazz Cafe Chain")
        self.assertEqual(restaurant.chain.owner, restaurant.contact)

    def test_cannot_add_restaurants_with_same_address(self):
        Restaurant.objects.create(
            address=self.address, name="JAzz", contact=self.restaurant_contact
        )
        with self.assertRaises(IntegrityError):
            Restaurant.objects.create(
                address=self.address, name="Bistro", contact=self.restaurant_contact
            )


class TestChainModel(TestBase):
    def setUp(self):
        super(TestChainModel, self).setUp()
        self.chain = Chain.objects.create(name="KFC", owner=self.restaurant_contact)
        self.address = Address.objects.create(
            city="Kezdivasarhely",
            street="Stadion",
            address="nr. 7, ap. 3",
            zip_code="525400",
            region="CV",
            country="Romania",
        )
        self.address2 = Address.objects.create(
            city="Kezdivasarhely",
            street="1 December",
            address="nr. 7, ap. 3",
            zip_code="525400",
            region="CV",
            country="Romania",
        )

    def test_chain_can_have_multiple_restaurants(self):
        Restaurant.objects.create(
            chain=self.chain,
            address=self.address,
            name="restaurant1",
            contact=self.restaurant_contact,
        )
        Restaurant.objects.create(
            chain=self.chain,
            address=self.address2,
            name="restaurant2",
            contact=self.restaurant_contact,
        )
        self.assertEqual(self.chain.restaurants.count(), 2)
