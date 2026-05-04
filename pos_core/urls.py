from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.http import JsonResponse

def api_root(request):
    return JsonResponse({"message": "POS API Working"})

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/', api_root),

    path('api/token/', TokenObtainPairView.as_view()),
    path('api/token/refresh/', TokenRefreshView.as_view()),

    path('api/accounts/', include('accounts.urls')),
    path('api/products/', include('products.urls')),
    path('api/sales/', include('sales.urls')),
]