# pos_core/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.http import JsonResponse

def home(request):
    return JsonResponse({"message": "Welcome to POS System"})

urlpatterns = [
    path('admin/', admin.site.urls),

    # JWT Authentication
    path('api/token/', TokenObtainPairView.as_view()),
    path('api/token/refresh/', TokenRefreshView.as_view()),

    # Apps
    path('api/accounts/', include('accounts.urls')),
    path('api/products/', include('products.urls')),
    path('api/sales/', include('sales.urls')),  # يحتوي على invoices و create

    # Home
    path('', home),
]