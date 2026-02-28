from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.sales_dashboard, name='sales_dashboard'),
    path('process-sale/', views.process_sale, name='process_sale'),
    path('add-stock/', views.add_stock, name='add_stock'),
    path('receipt/<str:order_id>/', views.receipt, name='receipt'),
    path('generate-report/', views.generate_report, name='generate_report'),
] 