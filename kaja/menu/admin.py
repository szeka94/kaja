from django.contrib import admin
from .models import Category, MenuItem
from django.contrib.auth.models import User, Group


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "restaurant", "is_active")
    list_filter = ("category__name", "restaurant__name")
    list_per_page = 20
