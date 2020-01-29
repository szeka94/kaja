from django.test import TestCase
from model_mommy import mommy

from kaja.restaurant.models import RestaurantContact


class TestBase(TestCase):
    def setUp(self):
        self.restaurant_contact = self.make(RestaurantContact)

    def make(self, model, commit=True, **kwargs):
        return mommy.make(model, **kwargs) if commit else mommy.prepare(model, **kwargs)
