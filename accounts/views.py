# accounts/views.py

# 🔹 Imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes

from django.utils import timezone
from django.contrib.auth.models import User

from .models import Shop, CustomUser, Customer
from .serializers import ShopSerializer


# 🔹 Create Shop
class ShopCreateView(generics.CreateAPIView):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer


# 🔹 Owner View
class OwnerOnlyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        shop = getattr(request.user, 'shop', None)
        return Response({
            "user": request.user.username,
            "shop": shop.name if shop else None
        })


# 🔹 Create User + Shop
@api_view(['POST'])
def create_shop_user(request):
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        shop_name = request.data.get('shop_name')

        if not username or not password or not shop_name:
            return Response({"error": "Missing fields"}, status=400)

        if CustomUser.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"}, status=400)

        user = CustomUser.objects.create_user(
            username=username,
            password=password
        )

        shop = Shop.objects.create(name=shop_name, owner=user)

        return Response({
            "message": "User and Shop created successfully",
            "user": username,
            "shop": shop.name
        })

    except Exception as e:
        return Response({"error": str(e)}, status=400)


# 🔹 Branches
@api_view(["GET"])
def branches(request):
    return Response([
        {"id": 1, "name": "Main Branch"},
        {"id": 2, "name": "Second Branch"}
    ])


# =========================================================
# 🔥 Customers APIs (نسخك كلها زي ما هي بس مترتبة)
# =========================================================

# 📋 customers_list (Version 1)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def customers_list(request):
    shop = request.user.shop
    customers = Customer.objects.filter(shop=shop).order_by("-created_at")

    data = []
    for c in customers:
        data.append({
            "id": c.id,
            "name": c.name,
            "phone": c.phone,
            "created_at": c.created_at.strftime("%Y-%m-%d %H:%M")
        })

    return Response(data)


# 📊 customers_stats (Version 1)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def customers_stats(request):
    shop = request.user.shop
    today = timezone.now().date()

    total = Customer.objects.filter(shop=shop).count()
    new_today = Customer.objects.filter(
        shop=shop,
        created_at__date=today
    ).count()

    percent = (new_today / total * 100) if total else 0

    return Response({
        "total": total,
        "new_today": new_today,
        "percent": round(percent, 2)
    })


# 📋 customers_list (Version 2)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def customers_list_v2(request):
    shop = request.user.shop
    customers = Customer.objects.filter(shop=shop).order_by("-created_at")

    data = [
        {
            "id": c.id,
            "name": c.name,
            "phone": c.phone,
            "created_at": c.created_at
        }
        for c in customers
    ]

    return Response(data)


# 📊 customers_stats (Version 2)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def customers_stats_v2(request):
    shop = request.user.shop
    total = Customer.objects.filter(shop=shop).count()

    today = timezone.now().date()
    new_today = Customer.objects.filter(
        shop=shop,
        created_at__date=today
    ).count()

    percent = (new_today / total * 100) if total > 0 else 0

    return Response({
        "total": total,
        "new_today": new_today,
        "percent": round(percent, 2)
    })


# =========================================================
# 🔥 check_or_create_customer (كل النسخ موجودة)
# =========================================================

# Version 1
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Shop, CustomUser, Customer
from .serializers import ShopSerializer, CustomerSerializer

# 🔹 Check or create customer
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_or_create_customer(request):
    name = request.data.get("name")
    phone = request.data.get("phone")
    shop = request.user.shop

    if not name or not phone:
        return Response({"error": "Missing customer name or phone"}, status=400)

    customer, created = Customer.objects.get_or_create(
        phone=phone,
        shop=shop,
        defaults={"name": name}
    )

    serializer = CustomerSerializer(customer)
    return Response(serializer.data)

# Version 2
@api_view(['POST'])
def check_or_create_customer_v2(request):
    data = request.data

    customer, created = Customer.objects.get_or_create(
        phone=data["phone"],
        defaults={
            "name": data["name"],
            "shop": request.user.shop
        }
    )

    serializer = CustomerSerializer(customer)
    return Response(serializer.data)


# Version 3
@api_view(['POST'])
def check_or_create_customer_v3(request):
    name = request.data.get("name")
    phone = request.data.get("phone")
    shop = request.user.shop

    customer, created = Customer.objects.get_or_create(
        phone=phone,
        defaults={
            "name": name,
            "shop": shop
        }
    )

    return Response({
        "id": customer.id,
        "created": created
    })