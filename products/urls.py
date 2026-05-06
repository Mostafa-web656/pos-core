from django.urls import path
from .views import products_view, product_detail

urlpatterns = [
    path('', products_view),  # 👉 ده /api/products/
    path('<int:id>/', product_detail),  # 👉 ده /api/products/1/
]