from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.utils import timezone
from django.db.models import Sum, F
from django.db.models.functions import TruncHour

import calendar
from decimal import Decimal

from products.models import Product
from .models import Sale, SaleItem
from accounts.models import Customer


# =========================
# PRODUCTS
# =========================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def products_api(request):
    user = request.user

    if not hasattr(user, 'shop') or not user.shop:
        return Response({"error": "User has no shop"}, status=400)

    data = request.data

    product = Product.objects.create(
        name=data["name"],
        price=data["price"],
        stock=data.get("stock", 0),
        shop=user.shop
    )

    return Response({
        "id": product.id,
        "name": product.name
    })


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_product(request, id):
    user = request.user

    try:
        product = Product.objects.get(id=id, shop=user.shop)
        product.delete()
        return Response({"status": "deleted"})
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)


# =========================
# CREATE SALE
# =========================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
@transaction.atomic
def create_sale(request):
    user = request.user

    if not hasattr(user, "shop") or not user.shop:
        return Response({"error": "User has no shop"}, status=400)

    shop = user.shop
    items = request.data.get("items", [])
    customer_id = request.data.get("customer")

    tax_rate = Decimal(request.data.get("tax_rate") or 0)

    if not items:
        return Response({"error": "No items provided"}, status=400)

    customer = None
    if customer_id:
        customer = Customer.objects.filter(id=customer_id, shop=shop).first()

    sale = Sale.objects.create(
        user=user,
        shop=shop,
        customer=customer,
        tax_rate=tax_rate,
        subtotal=0,
        tax_amount=0,
        total=0
    )

    subtotal = Decimal(0)

    for item in items:
        product = Product.objects.get(id=item["product_id"], shop=shop)
        qty = int(item["qty"])

        SaleItem.objects.create(
            sale=sale,
            product=product,
            qty=qty,
            price=product.price
        )

        subtotal += Decimal(product.price) * qty

        product.stock -= qty
        product.save()

    tax_amount = subtotal * tax_rate / Decimal("100")
    total = subtotal + tax_amount

    sale.subtotal = subtotal
    sale.tax_amount = tax_amount
    sale.total = total
    sale.save()

    return Response({
        "message": "Sale completed",
        "sale_id": sale.id,
        "total": float(total)
    })


# =========================
# DAILY REPORT
# =========================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def daily_report(request):
    shop = request.user.shop
    today = timezone.now().date()

    sales = Sale.objects.filter(created_at__date=today, shop=shop)

    total_sales = SaleItem.objects.filter(
        sale__in=sales
    ).aggregate(total=Sum(F("price") * F("qty")))["total"] or 0

    orders_count = sales.count()

    # 🔥 FIX مهم: hour بدل day
    chart = (
        sales
        .annotate(hour=TruncHour("created_at"))
        .values("hour")
        .annotate(total=Sum("total"))
        .order_by("hour")
    )

    chart_data = [
        {
            "hour": c["hour"].strftime("%H:%M"),
            "total": float(c["total"])
        }
        for c in chart
    ]

    return Response({
        "total_sales": float(total_sales),
        "orders": orders_count,
        "chart": chart_data
    })


# =========================
# MONTHLY REPORT
# =========================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def monthly_report(request):
    shop = request.user.shop
    month = int(request.GET.get("month", timezone.now().month))
    year = int(request.GET.get("year", timezone.now().year))

    sales = Sale.objects.filter(
        shop=shop,
        created_at__year=year,
        created_at__month=month
    )

    # 📊 إجمالي
    total = sales.aggregate(total=Sum("total"))["total"] or 0
    count = sales.count()

    average = total / count if count > 0 else 0

    # 📈 رسم يومي
    chart = (
        sales
        .annotate(day=TruncHour("created_at"))
        .values("day")
        .annotate(total=Sum("total"))
        .order_by("day")
    )

    chart_data = [
        {
            "day": c["day"].strftime("%Y-%m-%d %H:%M"),
            "total": float(c["total"])
        }
        for c in chart
    ]

    # 🔥 أفضل يوم
    best = sales.values("created_at__date").annotate(
        total=Sum("total")
    ).order_by("-total").first()

    best_day = {
        "day": str(best["created_at__date"]),
        "total": float(best["total"])
    } if best else None

    return Response({
        "total": float(total),
        "count": count,
        "average": float(average),
        "best_day": best_day,
        "chart": chart_data
    })

# =========================
# INVOICES
# =========================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def invoice_detail(request, id):
    shop = request.user.shop

    sale = Sale.objects.get(id=id, shop=shop)
    items = SaleItem.objects.filter(sale=sale)

    return Response({
        "id": sale.id,
        "date": sale.created_at.strftime("%Y-%m-%d %H:%M"),
        "customer_name": sale.customer.name if sale.customer else None,
        "customer_phone": sale.customer.phone if sale.customer else None,
        "total": float(sale.total),
        "items": [
            {
                "name": i.product.name,
                "qty": i.qty,
                "price": float(i.price),
                "total": float(i.qty * i.price)
            }
            for i in items
        ]
    })