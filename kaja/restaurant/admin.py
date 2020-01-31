from django.contrib import admin
from .models import Restaurant, Chain, RestaurantContact

# Register your models here.
admin.site.register(RestaurantContact)


class RestaurantAdmin(admin.StackedInline):
    model = Restaurant


@admin.register(Chain)
class ChainAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "restaurant_count")
    inlines = [RestaurantAdmin]

    def restaurant_count(self, obj):
        return obj.restaurants.count()
