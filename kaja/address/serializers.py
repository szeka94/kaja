from rest_framework import serializers

from kaja.address.models import Address


class AddressSerializer(serializers.ModelSerializer):
    is_restaurant_address = serializers.SerializerMethodField("get_is_restaurant_address")
    restaurant_id = serializers.SerializerMethodField("get_restaurant_id")

    class Meta:
        model = Address
        fields = "__all__"

    def get_is_restaurant_address(self, obj):
        return hasattr(obj, "restaurant")

    def get_restaurant_id(self, obj):
        if hasattr(obj, "restaurant"):
            return obj.restaurant.id

    def create(self, validated_data):
        address = super(AddressSerializer, self).create(validated_data)
        if self.context.get("user"):
            address.profile = self.context["user"].profile
        return address
