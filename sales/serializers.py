from rest_framework import serializers
from .models import Sale, SaleItem

class SaleItemSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="product.name")
    total = serializers.SerializerMethodField()

    class Meta:
        model = SaleItem
        fields = ["name", "qty", "price", "total"]

    def get_total(self, obj):
        return obj.qty * obj.price


class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source="customer.name", default=None)
    customer_phone = serializers.CharField(source="customer.phone", default=None)

    class Meta:
        model = Sale
        fields = [
            "id",
            "created_at",
            "subtotal",
            "tax_rate",
            "tax_amount",
            "total",
            "customer_name",
            "customer_phone",
            "items",
        ]