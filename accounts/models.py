from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import AbstractUser


class Customer(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)

    shop = models.ForeignKey("Shop", on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.phone}"
    
class CustomUser(AbstractUser):
    pass


class Shop(models.Model):
    name = models.CharField(max_length=200)

    owner = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="shop"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # 🔥 الاشتراك
    subscription_end = models.DateTimeField(null=True, blank=True)

    def is_active(self):
        return self.subscription_end and self.subscription_end > timezone.now()

    def activate(self, days=30):
        self.subscription_end = timezone.now() + timedelta(days=days)
        self.save()

    def __str__(self):
        return self.name