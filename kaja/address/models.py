from django.db import models

from core.mixin_model import TimestampMixin


class Address(models.Model, TimestampMixin):
    address = models.CharField(max_length=512)
    street = models.CharField(max_length=512)
    zip_code = models.CharField(max_length=10)
    formated_address = models.CharField(max_length=1024)
    city = models.CharField(max_length=256)  # CHANGE THIS TO A CHOICE-FIELD
    region = models.CharField(max_length=32)  # CHANGE THIS TO A CHOICE-FIELD
    country = models.CharField(max_length=32, default="Romania")  # CHANGE THIS TO A CHOICE-FIELD

    def save(self, *args, **kwargs):
        self.formated_address = (
            f"{self.street}/{self.address}, {self.city} {self.region} {self.zip_code}"
        )
        super(Address, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.city} - {self.zip_code}"
