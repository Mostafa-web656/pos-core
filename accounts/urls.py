#accounts\urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import OwnerOnlyView, create_shop_user, branches
from .views import customers_list, customers_stats,check_or_create_customer

urlpatterns = [
    path('owner-test/', OwnerOnlyView.as_view(), name="owner-test"),
    path('shops/add/', create_shop_user, name="shop-add"),
    path('owner/', OwnerOnlyView.as_view(), name="owner-only"),
    path('branches/', branches, name="branches"),

    # JWT endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path("customers/", customers_list),
    path("customers/stats/", customers_stats),
    path("customers/check_or_create/", check_or_create_customer),
   
]