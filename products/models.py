from django.db import models
from accounts.models import Shop


class Product(models.Model):
    UNIT_CHOICES = (
        ("piece", "Piece"),
        ("gram", "Gram"),
        ("liter", "Liter"),
    )

    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    # 🔥 المخزون (يدعم جرام / لتر / قطعة)
    stock = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    unit_type = models.CharField(
        max_length=10,
        choices=UNIT_CHOICES,
        default="piece"
    )

    # 🔥 حد التنبيه
    low_stock_alert = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=5
    )

    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    # =========================
    # 🔥 LOGIC (مهم جدًا)
    # =========================

    def decrease_stock(self, qty):
        """خصم آمن من المخزون"""
        if self.stock < qty:
            raise ValueError("Not enough stock")

        self.stock -= qty
        self.save()

    def is_low_stock(self):
        return self.stock <= self.low_stock_alert

    def is_out_of_stock(self):
        return self.stock <= 0

    def stock_status(self):
        if self.is_out_of_stock():
            return "OUT"
        elif self.is_low_stock():
            return "LOW"
        return "OK"

    def __str__(self):
        return f"{self.name} ({self.unit_type})"