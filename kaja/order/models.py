from decimal import Decimal
from django.db import models
from django.core.validators import ValidationError

from kaja.user.models import UserProfile
from kaja.address.models import Address
from core.mixin_model import TimestampMixin
from kaja.menu.models import OfferVariation
from kaja.restaurant.models import Restaurant


SERVICE_FEE_PERC = Decimal(0.1)
DELIVERY_PRICE_HARDCODED = Decimal(10)


class Order(models.Model, TimestampMixin):
    """
        Model for creating orders for multiple OfferVariations
    """

    PICKUP = "PCK"
    DELIVERY = "DLV"
    ORDER_TYPES = [(PICKUP, "Pickup"), (DELIVERY, "Delivery")]

    user = models.ForeignKey(
        UserProfile, null=True, on_delete=models.SET_NULL, related_name="orders"
    )
    variations = models.ManyToManyField(OfferVariation, related_name="orders")
    order_type = models.CharField(max_length=3, choices=ORDER_TYPES, default=DELIVERY)
    restaurant = models.ForeignKey(
        Restaurant, null=True, on_delete=models.SET_NULL, related_name="orders"
    )
    delivery_addess = models.ForeignKey(
        Address, null=True, on_delete=models.SET_NULL, related_name="orders"
    )

    def save(self, *args, **kwargs):
        super(Order, self).save(*args, **kwargs)
        if self.variations.exists():
            qs = (
                self.variations.prefetch_related("offer__restaurant")
                .values("offer__restaurant")
                .distinct()
            )
            if qs.count() > 1:
                raise ValidationError(
                    {"offer_variations": "Cannot create an order from two separate restaurants"}
                )
            if (
                not qs.first()["offer__restaurant"] == self.restaurant.id
            ):  # not sure if this is the proper way
                raise ValidationError(
                    {"restaurant": "Offer-variation and order restaurant differs"}
                )

    def needs_delivery(self):
        return self.order_type == self.DELIVERY

    def get_total_price(self):
        return self.payment.total

    def can_be_submitted(self):
        return self.variations.exists() and self.delivery_addess is not None


class OrderPayment(models.Model, TimestampMixin):
    """
        Keeps track of paid money to a given order
    """

    CARD_APP = "CRD"
    CASH_ON_DELIVERY = "COD"
    CASH_ON_PICKUP = "COP"
    CARD_ON_PICKUP = "CRP"
    PAYMENT_CHOICES = [
        (CARD_APP, "Card Payment"),
        (CASH_ON_DELIVERY, "Cash on Delivery"),
        (CASH_ON_PICKUP, "Cash on Pickup"),
        (CARD_ON_PICKUP, "Card on Pickup"),
    ]

    food_price = models.DecimalField(max_digits=10, decimal_places=3)
    delivery_fee = models.DecimalField(default=Decimal(0), max_digits=10, decimal_places=3)
    service_fee = models.DecimalField(default=Decimal(0), max_digits=10, decimal_places=3)
    payment_type = models.CharField(max_length=3, choices=PAYMENT_CHOICES, default=CARD_APP)
    total = models.DecimalField(max_digits=10, decimal_places=3)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")

    def clean(self, *args, **kwargs):
        """Custom validators here"""
        if self.order.order_type in [Order.PICKUP]:
            if self.delivery_fee > 0:  # if delivery set on pickup
                raise ValidationError({"delivery_fee": "Cannot be set if order_type is pickup"})
            if self.payment_type in [self.CASH_ON_DELIVERY]:
                raise ValidationError({"payment_type": "Cannot have COD payment on pickup"})
        if self.order.order_type in [Order.DELIVERY]:
            if self.payment_type in [self.CASH_ON_PICKUP, self.CARD_ON_PICKUP]:
                raise ValidationError(
                    {"payment_type": f"Cannot have {self.payment_type} on delivery"}
                )

        super(OrderPayment, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        """TODO: this needs a few testing!!!!!!!!!!"""
        self.delivery_fee = self.get_delivery_price()
        self.food_price = sum([var.price for var in self.order.variations.all()])
        if self.payment_type in [self.CARD_APP, self.CASH_ON_DELIVERY]:
            self.service_fee = round(self.food_price * SERVICE_FEE_PERC, 3)
        self.total = self.food_price + self.delivery_fee + self.service_fee
        self.full_clean()
        super(OrderPayment, self).save(*args, **kwargs)

    def get_delivery_price(self):
        return DELIVERY_PRICE_HARDCODED
