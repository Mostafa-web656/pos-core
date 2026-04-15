# accounts/admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Shop

User = get_user_model()  # هياخد CustomUser أو User حسب settings

@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active')
    search_fields = ('username', 'email')

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at')
    search_fields = ('name', 'owner__username')
