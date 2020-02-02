from kaja.user.models import User, UserProfile
from core.test_base import TestBase


class TestUserSignup(TestBase):
    @staticmethod
    def _init_registration_data():
        return {
            "email": "email_address@gmail.com",
            "password": "whatever",
            "profile": {"first_name": "Test", "last_name": "Andras", "phone_number": "0740501803"},
        }

    def test_endpoint_creates_user_and_userprofile(self):
        data = self._init_registration_data()
        resp = self.client.post("/api/signup/", data, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(resp.data["success"])
        self.assertEqual(resp.data["status_code"], 201)
        self.assertTrue(User.objects.filter(email="email_address@gmail.com").exists())
        self.assertTrue(UserProfile.objects.filter(user__email="email_address@gmail.com").exists())

    def test_endpoint_raises_error_if_missing_profile_data(self):
        data = self._init_registration_data()
        data.pop("profile")
        resp = self.client.post("/api/signup/", data, format="json")
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.data["status_code"], 400)
        self.assertFalse(resp.data["success"])
        self.assertTrue(
            "Cannot create user without user-profile information" in resp.data["data"]["profile"]
        )

    def test_endpoint_unique_user(self):
        self.make(User, email="email_address@gmail.com")
        data = self._init_registration_data()
        resp = self.client.post("/api/signup/", data, format="json")
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.data["status_code"], 400)
        self.assertTrue(
            "user with this email address already exists." in resp.data["data"]["email"]
        )


class TestUserLogin(TestBase):
    def setUp(self):
        super(TestUserLogin, self).setUp()
        self.user = User.objects.create_user(
            email="email_address@gmail.com", password="yoyoyoyoyoy"
        )
        self.user.save()
        self.user_profile = self.make(UserProfile, user=self.user)

    def test_user_can_login(self):
        data = {"email": self.user.email, "password": "yoyoyoyoyoy"}
        resp = self.client.post("/api/login/", data, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["status_code"], 200)
        self.assertTrue(resp.data["success"])
        self.assertTrue("token" in resp.data["data"])
        self.assertTrue("User logged in  successfully" in resp.data["data"]["message"])

    def test_user_cannot_login_with_incorrect_credintals(self):
        data = {"email": self.user.email, "password": "asdasdasdas"}
        resp = self.client.post("/api/login/", data, format="json")
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.data["status_code"], 400)
        self.assertTrue(
            "A user with this email and password is not found."
            in resp.data["data"]["non_field_errors"]
        )


class TestUserProfileView(TestBase):
    def test_unauthenticated_user_cannot_fetch_profile(self):
        resp = self.client.get("/api/profile/", format="json")
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(
            resp.data["data"]["detail"], "Authentication credentials were not provided."
        )
        self.assertEqual(resp.data["status_code"], 401)
        self.assertFalse(resp.data["success"])

    def test_authenticated_user_can_fetch_his_profile(self):
        resp = self.user_client.get("/api/profile/", format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["status_code"], 200)
        self.assertTrue(resp.data["success"])
        self.assertEqual(len(resp.data["data"]), 3)
        for col in ["first_name", "last_name", "phone_number"]:
            self.assertTrue(col in resp.data["data"])

    def test_authenticated_user_can_modify_its_profile(self):
        data = {"first_name": "Szerusz", "last_name": "Hey", "phone_number": "whatever"}
        resp = self.user_client.put("/api/profile/", data=data, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["data"], data)

    def test_authenticated_user_can_modify_profile_PATCH(self):
        data = {"first_name": "Szerusz"}
        resp = self.user_client.patch("/api/profile/", data, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["data"]["first_name"], "Szerusz")
        for col in ["last_name", "phone_number"]:
            self.assertTrue(col in resp.data["data"])

    def test_authenticated_user_can_delete_its_profile(self):
        resp = self.user_client.delete("/api/profile/", format="json")
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(resp.data["status_code"], 204)
        self.assertTrue(resp.data["success"])
