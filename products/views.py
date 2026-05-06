from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from products.models import Product
from .serializers import ProductSerializer


# =========================
# LIST & CREATE PRODUCTS
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def products_view(request):
    user = request.user

    if not hasattr(user, "shop") or not user.shop:
        return Response({"error": "User has no shop"}, status=400)

    if request.method == "GET":
        search = request.GET.get("search", "")

        products = Product.objects.filter(
            shop=user.shop,
            name__icontains=search
        ).order_by('-id')

        return Response([
            {
                "id": p.id,
                "name": p.name,
                "price": float(p.price),
                "stock": p.stock,
            }
            for p in products
        ])

    if request.method == "POST":
        try:
            data = request.data

            product = Product.objects.create(
                name=data["name"],
                price=data["price"],
                stock=data.get("stock", 0),
                shop=user.shop
            )

            return Response({
                "id": product.id,
                "name": product.name,
                "price": float(product.price),
                "stock": product.stock,
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)