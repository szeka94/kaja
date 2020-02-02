from kaja.user.models import User, UserProfile
from kaja.address.models import Address
from core.test_base import TestBase
from django.db.utils import IntegrityError


class TestUserModels(TestBase):
    def setUp(self):
        super(TestUserModels, self).setUp()
        self.addresses = [self.make(Address) for _ in range(3)]
        self.user = self.make(User)

    def test_user_can_have_profile(self):
        user = self.make(User)
        user_profile = self.make(UserProfile, user=user)
        self.assertEqual(user.profile, user_profile)
        self.assertEqual(user_profile.user, user)

    def test_user_profile_can_have_multiple_addresses(self):
        user_profile = self.make(UserProfile)
        user_profile.addresses.add(*self.addresses)
        user_profile.save()
        self.assertEqual(user_profile.addresses.count(), 3)

    def test_user_profile_cannot_be_created_without_user(self):
        with self.assertRaises(IntegrityError):
            UserProfile.objects.create(
                first_name="whatever", last_name="whatever2", phone_number="12345676"
            )
