from kaja.user.models import User, UserProfile
from kaja.address.models import Address
from kaja.restaurant.models import Restaurant
from core.test_base import TestBase


class TestAddress(TestBase):
    def setUp(self):
        super(TestAddress, self).setUp()
        self.u1, self.u2 = [self.make(User) for _ in range(2)]
        self.make(UserProfile, user=self.u1)
        self.make(UserProfile, user=self.u2)

    def _init_post_data(self):
        address = self.make(Address, commit=False).__dict__
        address.pop("_state")
        return address

    def test_unauthenticated_user_cannot_create_addresses(self):
        data = self._init_post_data()
        resp = self.client.post("/api/addresses/", data=data, format="json")
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(
            resp.data["data"]["detail"], "Authentication credentials were not provided."
        )
        self.assertEqual(resp.data["status_code"], 401)
        self.assertFalse(resp.data["success"])

    def test_autheticated_user_can_create_new_address(self):
        data = self._init_post_data()
        resp = self.user_client.post("/api/addresses/", data=data, format="json")
        self.assertEqual(resp.data["status_code"], 201)
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(resp.data["success"])
        self.assertFalse(resp.data["data"]["is_restaurant_address"])
        self.assertEqual(resp.data["data"]["profile"], self.user.profile.id)

    def test_users_cannot_see_each_others_addresses(self):
        self.make(Address, profile=self.u1.profile)
        resp = self.user_client.get("/api/addresses/", format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["status_code"], 200)
        self.assertFalse(bool(resp.data["data"]))

    def test_user_can_see_their_addresses(self):
        [self.make(Address, profile=self.user.profile) for _ in range(2)]
        resp = self.user_client.get("/api/addresses/", format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["status_code"], 200)
        self.assertFalse(resp.data["data"][0]["is_restaurant_address"])
        self.assertFalse(resp.data["data"][1]["is_restaurant_address"])
        self.assertEqual(len(resp.data["data"]), 2)

    def test_users_can_see_restaurant_addesses(self):
        address = self.make(Address)
        restaurant = self.make(Restaurant, address=address)
        resp = self.user_client.get("/api/addresses/", format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data["data"]), 1)
        self.assertTrue(resp.data["data"][0]["is_restaurant_address"])
        self.assertTrue(resp.data["data"][0]["profile"] is None)
        self.assertEqual(resp.data["data"][0]["restaurant_id"], restaurant.id)
