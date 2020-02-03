from django.db import models
from django.core.validators import ValidationError

from core.mixin_model import TimestampMixin
from core import constants as const
from kaja.user.models import UserProfile
from django.core.exceptions import ObjectDoesNotExist


class Address(models.Model, TimestampMixin):
    address = models.CharField(max_length=256)
    street = models.CharField(max_length=256)
    zip_code = models.CharField(max_length=10)
    formated_address = models.CharField(max_length=1024)
    city = models.CharField(
        max_length=256, choices=[(c.lower(), c) for c in const.SUPPORTED_CITIES]
    )
    region = models.CharField(
        max_length=32, choices=[(r.lower(), r) for r in const.SUPPORTED_REGIONS]
    )
    country = models.CharField(
        max_length=32,
        default="romania",
        choices=[(c.lower(), c) for c in const.SUPPORTED_COUNTRIES],
    )
    profile = models.ForeignKey(
        UserProfile, null=True, blank=True, on_delete=models.CASCADE, related_name="addresses"
    )

    def save(self, *args, **kwargs):
        self.formated_address = (
            f"{self.street}/{self.address}, {self.city} {self.region} {self.zip_code}"
        )
        self.full_clean()
        super(Address, self).save(*args, **kwargs)

    def clean(self):
        try:
            if self.profile and self.restaurant:
                raise ValidationError("Cannot have profile defined along with restaurant.")
        except ObjectDoesNotExist:
            pass

    def __str__(self):
        return f"{self.city} - {self.zip_code}"
