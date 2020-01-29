from django.db import models

from kaja.restaurant.models import Restaurant


class Category(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField()


class Offer(models.Model):
    """
        This is an offer a menu-tile for the end-user perspective. It can contain multiple
        menus with each different menu-variations
    """

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    image = models.ImageField("One and only image-field")
    name = models.CharField("Text shown to the buyer", max_length=128)
    description = models.TextField()

    def __str__(self):
        return self.name


class OfferVariation(models.Model):
    """
        This is a specific combination of menuitem-variations for a given offer (eg. small burger, big chips)
    """

    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name="variations")
    _price = models.FloatField(null=True)
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


class Extra(models.Model):
    """
        These are different extras at the end of checkout (like cheese, onion-rings etc)
    """

    name = models.CharField("Name of the extras stuff", max_length=128)
    additional_price = models.FloatField("Additional price to order")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="extras")
    offer_variations = models.ManyToManyField(OfferVariation, related_name="extras")

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="menu_items")
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        super(MenuItem, self).save(*args, **kwargs)
        if not self.variations.exists():
            variation = MenuItemVariation(
                name=self.name, description=self.description, menu_item=self
            )
            variation.save()


class MenuItemVariation(models.Model):
    variation_name = models.CharField(
        "Internal name of the menu-variation", default="default", max_length=128
    )
    name = models.CharField("Name to show to the clients", max_length=128)
    description = models.TextField(null=True)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name="variations")
    offer_variations = models.ManyToManyField(OfferVariation)

    class Meta:
        unique_together = ["menu_item", "variation_name"]
