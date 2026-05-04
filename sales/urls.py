from . import views   # ✅ مهم جدًا
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.http import JsonResponse

def api_root(request):
    return JsonResponse({"message": "POS API Working"})

urlpatterns = [
    path('admin/', admin.site.urls),

   # path('api/', api_root),  # 🔥 FIXED (بدل lambda الغبي)
   #path("invoices/", views.invoices),
    path("invoices/<int:id>/", views.invoice_detail),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('api/accounts/', include('accounts.urls')),
    path('api/products/', include('products.urls')),
    path('api/sales/', include('sales.urls')),
]