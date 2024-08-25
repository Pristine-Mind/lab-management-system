from django.urls import path
from . import views

urlpatterns = [
    path("add-medicine/", views.add_medicine, name="add_medicine"),
    path("add-batch/", views.add_batch, name="add_batch"),
    path("create-bill/", views.create_bill, name="create_bill"),
    path("print-bill/<int:pk>/", views.print_bill, name="bill_pdf"),
    path("replenish-stock/<int:batch_id>/", views.replenish_stock, name="replenish_stock"),
    path("low-stock-alerts/", views.low_stock_alerts, name="low_stock_alerts"),
    path("dashboard/", views.stock_dashboard, name="stock_dashboard"),
    path("medicine-list/", views.medicine_list, name="medicine_list"),
    path("batch-list/", views.batch_list, name="batch_list"),
]
