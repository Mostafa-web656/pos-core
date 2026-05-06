from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from products.models import Product
from accounts.models import Shop
from .serializers import ProductSerializer


def get_shop(user):
    return Shop.objects.filter(owner=user).first()

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def products_view(request):
    user = request.user

    # 🔥 حماية من crash لو مفيش shop
    if not hasattr(user, "shop") or user.shop is None:
        return Response(
            {"error": "User has no shop assigned"},
            status=400
        )

    shop = user.shop

    products = Product.objects.filter(shop=shop)

    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)