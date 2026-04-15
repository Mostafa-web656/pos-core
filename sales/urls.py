# sales/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.create_sale, name="create-sale"),
    path("products/", views.products_api, name="products"),
    path("products/<int:id>/", views.delete_product, name="delete-product"),
    path("invoices/", views.invoices, name="invoices"),
    path("reports/daily/", views.daily_report, name="daily-report"),
    path("reports/monthly/", views.monthly_report, name="monthly-report"),
]