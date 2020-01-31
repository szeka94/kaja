import datetime as dt
from django.db import models
from django.contrib.auth.models import User

from kaja.address.models import Address
from core.mixin_model import TimestampMixin


class RestaurantContact(User):
    class Meta:
        proxy = True

    def __str__(self):
        self.email


class Chain(models.Model, TimestampMixin):
    name = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(RestaurantContact, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Restaurant(models.Model, TimestampMixin):
    chain = models.ForeignKey(Chain, on_delete=models.CASCADE, related_name="restaurants")
    address = models.OneToOneField(Address, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    contact = models.ForeignKey(RestaurantContact, on_delete=models.CASCADE)
    start_hour = models.TimeField()
    end_hour = models.TimeField()
    is_card_payment = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.chain_id:
            self.chain = Chain(name=f"{self.name} Chain", owner=self.contact)
            self.chain.save()
        super(Restaurant, self).save(*args, **kwargs)

    @property
    def is_open(self):
        return self.start_hour < self._get_current_time() < self.end_hour

    @staticmethod
    def _get_current_time():
        return dt.datetime.now().time()

    def __str__(self):
        return f"{self.name} - {self.chain.name}"
