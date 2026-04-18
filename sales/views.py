# sales/views.py

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
# PRODUCTS API
# =========================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def products_api(request):
    """
    Create a new product for the authenticated user's shop.
    """
    user = request.user

    # Ensure the user is associated with a shop
    if not hasattr(user, 'shop') or not user.shop:
        return Response({"error": "User has no shop"}, status=400)

    data = request.data

    # Create the product
    product = Product.objects.create(
        name=data["name"],
        price=data["price"],
        stock=data.get("stock", 0),
        shop=user.shop
    )

    return Response({
        "id": product.id,
        "name": product.name,
        "shop": user.shop.name
    })


@csrf_exempt
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_product(request, id):
    """
    Delete a product belonging to the authenticated user's shop.
    """
    user = request.user

    try:
        product = Product.objects.get(id=id, shop=user.shop)
        product.delete()
        return JsonResponse({"status": "deleted"})
    except Product.DoesNotExist:
        return JsonResponse({"error": "Product not found"}, status=404)



# =========================
# CREATE SALE (FIXED)
# =========================
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@transaction.atomic
def create_sale(request):
    try:
        user = request.user

        if not hasattr(user, "shop") or not user.shop:
            return Response({"error": "User has no shop"}, status=400)

        shop = user.shop

        items = request.data.get("items") or []
        customer_id = request.data.get("customer")

        # ✅ FIX: Decimal tax_rate
        try:
            tax_rate = Decimal(request.data.get("tax_rate") or 0)
        except:
            return Response({"error": "Invalid tax_rate"}, status=400)

        if len(items) == 0:
            return Response({"error": "No items provided"}, status=400)

        # customer
        customer = None
        if customer_id:
            customer = Customer.objects.filter(id=customer_id, shop=shop).first()

        subtotal = Decimal(0)

        # create sale
        sale = Sale.objects.create(
            user=user,
            shop=shop,
            customer=customer,
            tax_rate=tax_rate,
            subtotal=0,
            tax_amount=0,
            total=0
        )

        # items loop
        for item in items:
            product_id = item.get("product_id")
            qty = item.get("qty")

            if not product_id:
                return Response({"error": "Missing product_id"}, status=400)

            try:
                product = Product.objects.get(id=product_id, shop=shop)
            except Product.DoesNotExist:
                return Response({"error": f"Product {product_id} not found"}, status=404)

            try:
                qty = int(qty)
            except:
                return Response({"error": "Invalid quantity"}, status=400)

            if qty <= 0:
                return Response({"error": "Invalid quantity"}, status=400)

            if product.stock < qty:
                return Response({"error": f"Not enough stock for {product.name}"}, status=400)

            SaleItem.objects.create(
                sale=sale,
                product=product,
                qty=qty,
                price=product.price
            )

            subtotal += Decimal(product.price) * Decimal(qty)

            product.stock -= qty
            product.save()

        # ✅ FIX Decimal math
        tax_amount = subtotal * tax_rate / Decimal("100")
        total = subtotal + tax_amount

        sale.subtotal = subtotal
        sale.tax_amount = tax_amount
        sale.total = total
        sale.save()

        return Response({
            "message": "Sale completed",
            "sale_id": sale.id,
            "subtotal": float(subtotal),
            "tax_rate": float(tax_rate),
            "tax_amount": float(tax_amount),
            "total": float(total)
        })

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return Response({"error": str(e)}, status=500)


# =========================
# DAILY REPORT
# =========================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def daily_report(request):
    user = request.user

    if not hasattr(user, "shop") or user.shop is None:
        return Response({"error": "User has no shop"}, status=400)

    today = timezone.now().date()
    shop = user.shop

    sales = Sale.objects.filter(created_at__date=today, shop=shop)

    total_sales = (
        SaleItem.objects.filter(sale__in=sales)
        .aggregate(total=Sum(F("price") * F("qty")))
    )["total"] or 0

    orders = sales.count()

    chart_qs = (
        SaleItem.objects.filter(sale__in=sales)
        .annotate(hour=TruncHour("sale__created_at"))
        .values("hour")
        .annotate(total=Sum(F("price") * F("qty")))
        .order_by("hour")
    )

    chart_data = [
        {
            "hour": c["hour"].strftime("%H:%M"),
            "total": float(c["total"])
        }
        for c in chart_qs
    ]

    return Response({
        "total_sales": float(total_sales),
        "orders": orders,
        "chart": chart_data
    })


# =========================
# MONTHLY REPORT
# =========================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def monthly_report(request):
    month = int(request.GET.get("month", timezone.now().month))
    year = int(request.GET.get("year", timezone.now().year))
    shop = request.user.shop

    sales = Sale.objects.filter(
        created_at__year=year,
        created_at__month=month,
        shop=shop
    )

    total = sales.aggregate(total=Sum("total"))["total"] or 0
    count = sales.count()
    avg = total / count if count else 0

    days_in_month = calendar.monthrange(year, month)[1]

    chart = []
    for day in range(1, days_in_month + 1):
        day_total = Sale.objects.filter(
            created_at__year=year,
            created_at__month=month,
            created_at__day=day,
            shop=shop
        ).aggregate(total=Sum("total"))["total"] or 0

        chart.append({"day": day, "total": float(day_total)})

    return Response({
        "total": float(total),
        "count": count,
        "average": float(avg),
        "chart": chart
    })


# =========================
# INVOICES
# =========================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def invoices(request):
    shop = request.user.shop

    sales = Sale.objects.filter(shop=shop).order_by("-created_at")

    if request.GET.get("year"):
        sales = sales.filter(created_at__year=request.GET.get("year"))

    if request.GET.get("month"):
        sales = sales.filter(created_at__month=request.GET.get("month"))

    if request.GET.get("day"):
        sales = sales.filter(created_at__day=request.GET.get("day"))

    data = []
    for sale in sales:
        data.append({
            "id": sale.id,
        
            "date": sale.created_at.strftime("%Y-%m-%d %H:%M"),
            "customer_name": sale.customer.name if sale.customer else None,
            "customer_phone": sale.customer.phone if sale.customer else None,
            "subtotal": float(sale.subtotal),
            "tax_rate": float(sale.tax_rate),
            "tax_amount": float(sale.tax_amount),
            "total": float(sale.total),
            "items": [
                {
                    "name": i.product.name,
                    "qty": i.qty,
                    "price": float(i.price),
                    "total": float(i.price * i.qty),
                }
                for i in sale.items.all()
            ]
        })

    return Response(data)