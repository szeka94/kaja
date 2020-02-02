from kaja.user.serializers import UserSerializer, UserRegistrationSerializer, UserLoginSerializer
from kaja.user.models import User, UserProfile
from core.test_base import TestBase


class TestUserSerializer(TestBase):
    def setUp(self):
        super(TestUserSerializer, self).setUp()
        self.user = self.make(User)

    def test_user_serializer_creates_user_profile(self):
        serializer = UserSerializer(
            data={"first_name": "Some", "last_name": "User", "phone_number": "072301201"}
        )
        self.assertTrue(serializer.is_valid())


class TestUserRegistrationSerializer(TestBase):
    def test_user_registration_serializer_creates_user_profile(self):
        data = {
            "email": "email_address@address.com",
            "password": "some_password",
            "profile": {
                "first_name": "FirstName",
                "last_name": "LastName",
                "phone_number": "1234567898",
            },
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertTrue(User.objects.filter(email="email_address@address.com").exists())
        self.assertTrue(
            UserProfile.objects.filter(user__email="email_address@address.com").exists()
        )


class TestUserLoginSerializer(TestBase):
    def setUp(self):
        super(TestUserLoginSerializer, self).setUp()

    def test_raises_validation_error_on_not_found_user(self):
        serializer = UserLoginSerializer(
            data=dict(email="not_found@email.com", password="password")
        )
        self.assertFalse(serializer.is_valid())
        self.assertTrue(
            "A user with this email and password is not found."
            in serializer.errors["non_field_errors"]
        )

    def test_serializers_returns_email_and_token(self):
        serializer = UserLoginSerializer(
            data={"email": self.user.email, "password": self.user_password}
        )
        self.assertTrue(serializer.is_valid())
        self.assertTrue("token" in serializer.validated_data)
        self.assertTrue("email" in serializer.validated_data)
