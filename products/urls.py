from django.urls import path
from .views import products_view
from .views import products_view, product_detail
urlpatterns = [
    path('', products_view, name='product-list'),  # <- خليها فاضية
    path('products/', products_view, name='products'),
    path('products/<int:id>/', product_detail, name='product_detail'),
]