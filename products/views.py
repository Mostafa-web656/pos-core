from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from products.models import Product
from .serializers import ProductSerializer


# =========================
# HELPER
# =========================
def get_shop(user):
    return getattr(user, "shop", None)


# =========================
# LIST & CREATE PRODUCTS
# =========================
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def products_view(request):
    user = request.user
    shop = get_shop(user)

    if not shop:
        return Response({"error": "User has no shop"}, status=400)

    search = request.GET.get("search", "")

    # 🔍 GET PRODUCTS
    if request.method == 'GET':
        products = Product.objects.filter(
            shop=shop,
            name__icontains=search
        ).order_by('-id')

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    # ➕ CREATE PRODUCT
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(shop=shop)
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)


# =========================
# UPDATE & DELETE PRODUCT
# =========================
@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def product_detail(request, id):
    user = request.user
    shop = get_shop(user)

    if not shop:
        return Response({"error": "User has no shop"}, status=400)

    try:
        product = Product.objects.get(id=id, shop=shop)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)

    # ✏️ UPDATE
    if request.method == 'PUT':
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    # 🗑 DELETE
    product.delete()
    return Response({"message": "Product deleted successfully"})