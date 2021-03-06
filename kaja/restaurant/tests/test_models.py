import mock
import datetime as dt
from django.db.utils import IntegrityError

from kaja.restaurant.models import Restaurant, Address, Chain
from core.test_base import TestBase


class TestRestaurantModel(TestBase):
    def setUp(self):
        super(TestRestaurantModel, self).setUp()
        self.address = Address.objects.create(
            city="kezdivasarhely",
            street="Stadion",
            address="nr. 7, ap. 3",
            zip_code="525400",
            region="cv",
            country="romania",
        )

    def test_restaurant_creates_default_chain(self):
        restaurant = Restaurant.objects.create(
            address=self.address,
            name="Jazz Cafe",
            contact=self.restaurant_contact,
            start_hour=dt.time(8, 00),
            end_hour=dt.time(20, 00),
        )
        self.assertEqual(restaurant.chain.name, "Jazz Cafe Chain")
        self.assertEqual(restaurant.chain.owner, restaurant.contact)

    def test_cannot_add_restaurants_with_same_address(self):
        self.make(Restaurant, address=self.address, name="JAzz", contact=self.restaurant_contact)
        with self.assertRaises(IntegrityError):
            Restaurant.objects.create(
                address=self.address, name="Bistro", contact=self.restaurant_contact
            )

    @mock.patch("kaja.restaurant.models.Restaurant._get_current_time")
    def test_is_open_property(self, mock_datetime):
        restaurant = self.make(Restaurant, start_hour=dt.time(8, 0), end_hour=dt.time(20, 0))
        mock_datetime.return_value = dt.time(10, 0)
        self.assertEqual(restaurant.is_open, True)
        mock_datetime.return_value = dt.time(6, 0)
        self.assertEqual(restaurant.is_open, False)
        mock_datetime.return_value = dt.time(21, 0)
        self.assertEqual(restaurant.is_open, False)


class TestChainModel(TestBase):
    def setUp(self):
        super(TestChainModel, self).setUp()
        self.chain = Chain.objects.create(name="KFC", owner=self.restaurant_contact)
        self.address = Address.objects.create(
            city="kezdivasarhely",
            street="Stadion",
            address="nr. 7, ap. 3",
            zip_code="525400",
            region="cv",
            country="romania",
        )
        self.address2 = Address.objects.create(
            city="kezdivasarhely",
            street="1 December",
            address="nr. 7, ap. 3",
            zip_code="525400",
            region="cv",
            country="romania",
        )

    def test_chain_can_have_multiple_restaurants(self):
        self.make(
            Restaurant,
            chain=self.chain,
            address=self.address,
            name="restaurant1",
            contact=self.restaurant_contact,
        )
        self.make(
            Restaurant,
            chain=self.chain,
            address=self.address2,
            name="restaurant2",
            contact=self.restaurant_contact,
        )
        self.assertEqual(self.chain.restaurants.count(), 2)
