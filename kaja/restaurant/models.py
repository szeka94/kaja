from django.db import models
from django.contrib.auth.models import User

from kaja.address.models import Address


class RestaurantContact(User):
    class Meta:
        proxy = True

    def __str__(self):
        self.email


class Chain(models.Model):
    name = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(RestaurantContact, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Restaurant(models.Model):
    chain = models.ForeignKey(Chain, on_delete=models.CASCADE, related_name="restaurants")
    address = models.OneToOneField(Address, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    contact = models.ForeignKey(RestaurantContact, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.chain_id:
            self.chain = Chain(name=f"{self.name} Chain", owner=self.contact)
            self.chain.save()
        super(Restaurant, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.chain.name}"
