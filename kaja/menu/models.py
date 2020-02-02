from django.db import models

from kaja.restaurant.models import Restaurant
from core.mixin_model import TimestampMixin


class Category(models.Model, TimestampMixin):
    name = models.CharField(max_length=128)
    description = models.TextField()

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Offer(models.Model, TimestampMixin):
    """
        This is an offer a menu-tile for the end-user perspective. It can contain multiple
        menus with each different menu-variations
    """

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    image = models.ImageField("One and only image-field")
    name = models.CharField("Text shown to the buyer", max_length=128)
    description = models.TextField()

    def save(self, *args, **kwargs):
        super(Offer, self).save(*args, **kwargs)
        # TODO: ask for help for this stuff...
        """It would be nice to create the all the offervariations on initialization from the menuitems"""

    def __str__(self):
        return self.name


class OfferVariation(models.Model, TimestampMixin):
    """
        TODO:
        This is a specific combination of menuitem-variations for a given offer (eg. small burger, big chips)
    """

    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name="variations")
    _price = models.DecimalField(null=True, max_digits=10, decimal_places=3)
    _is_active = models.BooleanField(default=True)

    @property
    def is_active(self):
        if not self.price:
            return False
        return self._is_active

    @is_active.setter
    def is_active(self, value):
        self._is_active = value

    @property
    def price(self):
        extra_cost = sum(self.extras.values_list("additional_price", flat=True))
        if extra_cost:
            return self._price + extra_cost
        return self._price

    @price.setter
    def price(self, value):
        self._price = value


class Extra(models.Model, TimestampMixin):
    """
        These are different extras at the end of checkout (like cheese, onion-rings etc)
    """

    name = models.CharField("Name of the extras stuff", max_length=128)
    additional_price = models.DecimalField(
        "Additional price to order", max_digits=10, decimal_places=3
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="extras")
    offer_variations = models.ManyToManyField(OfferVariation, related_name="extras")

    def __str__(self):
        return self.name


class MenuItem(models.Model, TimestampMixin):
    """
        Stores general information about menu-items, used to build offers.
    """

    name = models.CharField(max_length=128)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="menu_items")
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    offers = models.ManyToManyField(Offer, blank=True, related_name="menu_items")
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        super(MenuItem, self).save(*args, **kwargs)
        if not self.variations.exists():
            variation = MenuItemVariation(
                name=self.name, description=self.description, menu_item=self, is_default=True
            )
            variation.save()

    def __str__(self):
        return self.name


class MenuItemVariation(models.Model, TimestampMixin):
    """
        Different variations of a given menu-item. Like size.. etc..
    """

    variation_name = models.CharField(
        "Internal name of the menu-variation", default="default", max_length=128
    )
    name = models.CharField("Name to show to the clients", max_length=128)
    description = models.TextField(null=True)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name="variations")
    offer_variations = models.ManyToManyField(OfferVariation)
    is_default = models.BooleanField(default=False)

    class Meta:
        unique_together = ["menu_item", "variation_name"]
        # TODO: play around with this and find a way to constrain the creation of 2 defualt=True
        #       models for the same menuitem
        constraints = [
            models.UniqueConstraint(
                fields=["menu_item", "is_default"],
                condition=models.Q(is_default=True),
                name="only_one_default",
            )
        ]

    def __str__(self):
        return f"{self.variation_name} - {self.name}"
