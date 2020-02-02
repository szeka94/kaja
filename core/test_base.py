from django.test import TestCase
from rest_framework.test import APIClient
from model_mommy import mommy

from kaja.user.models import User, UserProfile
from kaja.restaurant.models import RestaurantContact


class TestBase(TestCase):
    def setUp(self):
        self.restaurant_contact = self.make(RestaurantContact)
        self.client = APIClient()
        self.user_password = "blablabla"
        self.user = User.objects.create_user(email="email@email.com", password=self.user_password)
        self.make(UserProfile, user=self.user)
        self.user_client = APIClient()
        self.user_client.force_authenticate(user=self.user)

    def make(self, model, commit=True, **kwargs):
        return mommy.make(model, **kwargs) if commit else mommy.prepare(model, **kwargs)
