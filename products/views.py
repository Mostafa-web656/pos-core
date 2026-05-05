from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from products.models import Product
from .serializers import ProductSerializer


# =========================
# LIST & CREATE PRODUCTS
# =========================
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def products_view(request):
    user = request.user

    if not hasattr(user, "shop") or not user.shop:
        return Response({"error": "User has no shop"}, status=400)

    search = request.GET.get("search", "")

    # ======================
    # GET PRODUCTS
    # ======================
    if request.method == 'GET':
        products = Product.objects.filter(
            shop=user.shop,
            name__icontains=search
        ).order_by('-id')

        serializer = ProductSerializer(products, many=True)

        # 🔥 إضافة status ذكي للفورنت
        data = serializer.data
        for item, product in zip(data, products):
            item["stock_status"] = product.stock_status()
            item["is_low_stock"] = product.is_low_stock()
            item["is_out_of_stock"] = product.is_out_of_stock()
            item["unit_type"] = product.unit_type

        return Response(data)

    # ======================
    # CREATE PRODUCT
    # ======================
    if request.method == 'POST':
        serializer = ProductSerializer(data=request.data)

        if serializer.is_valid():
            product = serializer.save(shop=user.shop)

            return Response({
                **ProductSerializer(product).data,
                "stock_status": product.stock_status(),
                "is_low_stock": product.is_low_stock(),
                "is_out_of_stock": product.is_out_of_stock(),
            }, status=201)

        return Response(serializer.errors, status=400)


# =========================
# UPDATE & DELETE PRODUCT
# =========================
@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def product_detail(request, id):
    user = request.user

    if not hasattr(user, "shop") or not user.shop:
        return Response({"error": "User has no shop"}, status=400)

    try:
        product = Product.objects.get(id=id, shop=user.shop)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)

    # ✏️ UPDATE
    if request.method == 'PUT':
        serializer = ProductSerializer(product, data=request.data, partial=True)

        if serializer.is_valid():
            product = serializer.save()

            return Response({
                **ProductSerializer(product).data,
                "stock_status": product.stock_status(),
                "is_low_stock": product.is_low_stock(),
                "is_out_of_stock": product.is_out_of_stock(),
            })

        return Response(serializer.errors, status=400)

    # 🗑 DELETE
    if request.method == 'DELETE':
        product.delete()
        return Response({"message": "Product deleted successfully"})