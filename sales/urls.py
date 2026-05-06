from django.urls import path
from . import views
from django.http import JsonResponse

def sales_root(request):
    return JsonResponse({"message": "Sales API working"})

urlpatterns = [
    path("", sales_root),

    # ✅ products
    path("products/", views.products_api),
    path("products/<int:id>/", views.delete_product),

    # ✅ create sale
    path("create/", views.create_sale),

    # ✅ invoices
    #path("invoices/", views.invoices),
    #path("invoices/<int:id>/", views.invoice_detail),

    # ✅ reports
    path("reports/daily/", views.daily_report),
    path("reports/monthly/", views.monthly_report),
]