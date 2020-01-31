from django.db.utils import IntegrityError
from core.test_base import TestBase
from kaja.menu.models import MenuItem, MenuItemVariation, Offer, OfferVariation, Category, Extra
from kaja.restaurant.models import Restaurant


class MenuTestBase(TestBase):
    def setUp(self):
        super(MenuTestBase, self).setUp()
        self.restaurant = self.make(Restaurant, name="Bely Food")
        self.burger = self.make(MenuItem, name="Pulled Pork", restaurant=self.restaurant)
        self.big_burger = self.make(
            MenuItemVariation, variation_name="big", name="Big burger", menu_item=self.burger
        )
        self.small_burger = self.make(
            MenuItemVariation, variation_name="small", name="Small burger", menu_item=self.burger
        )

        self.chips = self.make(MenuItem, name="Potato chips", restaurant=self.restaurant)
        self.large_chips = self.make(
            MenuItemVariation, variation_name="large", name="Large Potato", menu_item=self.chips
        )
        self.small_chips = self.make(
            MenuItemVariation, variation_name="small", name="Small Potato", menu_item=self.chips
        )
        self.offer = self.make(Offer, restaurant=self.restaurant)


class TestOfferVariation(MenuTestBase):
    def setUp(self):
        super(TestOfferVariation, self).setUp()
        sos = Category.objects.create(name="Extra sos", description="Add sos to your stuff")
        self.garlic_cream = Extra.objects.create(
            name="Garlic soos", additional_price=2, category=sos
        )
        self.ketchup = Extra.objects.create(name="Ketchup", additional_price=3, category=sos)

    def test_menu_item_variations_can_be_added_to_offer_variations(self):
        offer_variation = self.make(OfferVariation, offer=self.offer, price=21)
        offer_variation.menuitemvariation_set.add(self.big_burger)
        offer_variation.menuitemvariation_set.add(self.small_chips)
        self.assertEqual(offer_variation.menuitemvariation_set.count(), 2)
        self.assertEqual(self.big_burger.offer_variations.count(), 1)
        self.assertEqual(self.small_chips.offer_variations.count(), 1)
        self.assertEqual(self.offer.variations.count(), 1)

    def test_offer_variation_is_not_active_if_no_price_provided(self):
        offer_variation = self.make(OfferVariation, offer=self.offer, is_active=True)
        self.assertEqual(offer_variation.is_active, False)

    def test_extras_can_be_added_to_offer_variations(self):
        offer_variation = self.make(OfferVariation, offer=self.offer, price=21)
        offer_variation.menuitemvariation_set.add(self.big_burger)
        offer_variation.menuitemvariation_set.add(self.small_chips)
        offer_variation.extras.add(self.garlic_cream)
        offer_variation.extras.add(self.ketchup)
        self.assertEqual(offer_variation.extras.count(), 2)
        self.assertEqual(
            offer_variation.price,
            21 + self.garlic_cream.additional_price + self.ketchup.additional_price,
        )


class TestMenuItemModel(MenuTestBase):
    def test_creating_menu_item_creates_default_menu_item_variation(self):
        item = self.make(MenuItem, name="test menu item", description="test description")
        self.assertEqual(item.variations.count(), 1)
        var = item.variations.first()
        self.assertEqual(var.variation_name, "default")
        self.assertEqual(var.name, "test menu item")
        self.assertEqual(var.description, "test description")
        self.assertEqual(var.is_default, True)

    def test_menu_item_keeps_default_if_other_is_provided(self):
        item = self.make(MenuItem)
        item.variations.add(self.make(MenuItemVariation, variation_name="first", menu_item=item))
        item.variations.add(self.make(MenuItemVariation, variation_name="second", menu_item=item))
        self.assertEqual(item.variations.count(), 3)
        self.assertEqual(
            sorted(item.variations.values_list("variation_name", flat=True)),
            ["default", "first", "second"],
        )

    def test_menu_item_can_access_restaurant(self):
        item = self.make(MenuItem, restaurant=self.restaurant)
        self.assertEqual(item.restaurant, self.restaurant)

    def test_only_one_default_menu_item_variation_for_each_menu_item(self):
        item = self.make(MenuItem)
        self.assertEqual(item.variations.first().is_default, True)
        with self.assertRaises(IntegrityError):
            item.variations.add(
                self.make(
                    MenuItemVariation, variation_name="another-def", menu_item=item, is_default=True
                )
            )

    def test_not_default_variations_can_be_added_to_item(self):
        item = self.make(MenuItem)
        self.make(MenuItemVariation, variation_name="whatever", menu_item=item, is_default=False)
        var = item.variations.get(variation_name="default")
        var.is_default = False
        var.save()
        self.make(MenuItemVariation, variation_name="whatever2", menu_item=item, is_default=True)
        self.assertEqual(item.variations.filter(is_default=True).count(), 1)


class TestOfferModel(MenuTestBase):
    def test_offer_creates_default_offervariations_from_menuitems(self):
        offer = self.make(Offer, restaurant=self.restaurant)
        offer.menu_items.add(self.burger, self.chips)
        offer.save()
        self.assertEqual(offer.menu_items.count(), 2)
        self.assertEqual(offer.variations.count(), 6)
        self.assertEqual(
            offer.variations.values_list("is_active", flat=True), [False for _ in range(6)]
        )
