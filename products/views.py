from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from products.models import Product
from accounts.models import Shop
from .serializers import ProductSerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def products_view(request):
    user = request.user

    # ✅ استخدم الدالة الصح
    shop = Shop.objects.filter(owner=user).first()

    if not shop:
        return Response({"error": "No shop found for this user"}, status=400)

    # ================= GET =================
    if request.method == "GET":
        search = request.GET.get("search", "")

        products = Product.objects.filter(
            shop=shop,
            name__icontains=search
        ).order_by("-id")

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    # ================= POST =================
    if request.method == "POST":
        data = request.data

        product = Product.objects.create(
            name=data["name"],
            price=data["price"],
            stock=data.get("stock", 0),
            shop=shop
        )

        return Response(ProductSerializer(product).data)