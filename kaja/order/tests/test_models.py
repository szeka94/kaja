from decimal import Decimal
from kaja.user.models import UserProfile
from django.core.validators import ValidationError

from core.test_base import TestBase
from kaja.address.models import Address
from kaja.menu.models import OfferVariation
from kaja.restaurant.models import Restaurant
from kaja.order.models import Order, OrderPayment


class TestOrderModel(TestBase):
    def setUp(self):
        super(TestOrderModel, self).setUp()
        self.user = self.make(UserProfile)
        self.restaurant = self.make(Restaurant)
        self.restaurant2 = self.make(Restaurant)
        self.variation = self.make(OfferVariation, price=10)

    def test_order_is_still_exists_if_user_deleted(self):
        user = self.make(UserProfile)
        order = self.make(Order, user=user)
        self.assertEqual(user.orders.count(), 1)
        user.delete()
        self.assertEqual(Order.objects.count(), 1)
        order.refresh_from_db()
        self.assertTrue(not order.user)

    def test_order_need_delivery(self):
        order = self.make(Order, order_type=Order.PICKUP)
        self.assertEqual(order.needs_delivery(), False)
        order.order_type = Order.DELIVERY
        order.save()
        self.assertEqual(order.needs_delivery(), True)

    def test_order_payment_calculates_total_payment(self):
        var1, var2 = [self.make(OfferVariation, price=10) for _ in range(2)]
        order = self.make(Order, order_type=Order.DELIVERY)
        order.variations.add(var1, var2)
        self.make(OrderPayment, payment_type=OrderPayment.CARD_APP, order=order)
        self.assertEqual(float(order.get_total_price()), 32)
        self.assertEqual(order.payment.food_price, Decimal("20"))
        self.assertEqual(float(order.payment.service_fee), 2.0)

    def test_cannot_create_order_if_ordering_from_multiple_restaurants(self):
        restaurants = [self.make(Restaurant) for _ in range(2)]
        var1, var2 = [self.make(OfferVariation, price=10, offer__restaurant=r) for r in restaurants]
        order = self.make(Order, order_type=Order.DELIVERY)
        with self.assertRaises(ValidationError):
            order.variations.add(var1, var2)
            order.save()

    def test_cannot_create_order_without_at_least_one_offer_variation_and_address(self):
        order = Order(user=self.user, restaurant=self.restaurant)
        order.save()
        self.assertEqual(order.can_be_submitted(), False)
        self.variation.offer.restaurant = self.restaurant
        self.variation.offer.save()
        order.variations.add(self.variation)
        self.assertEqual(order.can_be_submitted(), False)
        order.delivery_addess = self.make(Address)
        order.save()
        self.assertEqual(order.can_be_submitted(), True)

    def test_offer_variation_restaurant_needs_to_be_order_restaurant(self):
        order = self.make(Order, restaurant=self.restaurant)
        var1, var2 = [
            self.make(OfferVariation, price=10, offer__restaurant=self.restaurant2)
            for _ in range(2)
        ]
        order.variations.add(var1, var2)
        with self.assertRaises(ValidationError):
            order.save()


class TestOrderPaymentModel(TestBase):
    def setUp(self):
        self.order = self.make(Order)
        self.in_app_payments = [OrderPayment.CARD_APP, OrderPayment.CASH_ON_DELIVERY]
        self.in_rest_payment = [OrderPayment.CARD_ON_PICKUP, OrderPayment.CASH_ON_PICKUP]

    def test_order_payment_raises_error_if_delivery_fee_on_pickup(self):
        self.order.order_type = Order.PICKUP
        self.order.save()
        with self.assertRaises(ValidationError):
            self.make(
                OrderPayment,
                order=self.order,
                payment_type=OrderPayment.CASH_ON_PICKUP,
                delivery_fee=Decimal(10),
            )

    def test_order_payment_raises_error_mixed_order_type_payment_choices(self):
        self.order.order_type = Order.PICKUP
        self.order.save()
        for invalid_payment in self.in_app_payments:
            with self.assertRaises(ValidationError):
                self.make(OrderPayment, order=self.order, payment_type=invalid_payment)
        self.order.order_type = Order.DELIVERY
        self.order.save()
        for invalid_payment in self.in_rest_payment:
            with self.assertRaises(ValidationError):
                self.make(OrderPayment, order=self.order, payment_type=invalid_payment)

    def test_cannot_create_CRP_payment_if_restaurant_takes_no_card(self):
        restaurant = self.make(Restaurant, is_card_payment=False)
        order = self.make(Order, restaurant=restaurant, order_type=Order.PICKUP)
        with self.assertRaises(ValidationError):
            self.make(OrderPayment, order=order, payment_type=OrderPayment.CARD_ON_PICKUP)
