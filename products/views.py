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
    shop = get_shop(user)

    # 🔥 أهم سطر يمنع 500 نهائيًا
    if not shop:
        return Response([], status=200)

    search = request.GET.get("search", "")

    if request.method == 'GET':
        products = Product.objects.filter(shop=shop)

        if search:
            products = products.filter(name__icontains=search)

        serializer = ProductSerializer(products.order_by('-id'), many=True)
        return Response(serializer.data)

    serializer = ProductSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save(shop=shop)
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)