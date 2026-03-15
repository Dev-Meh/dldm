from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # User management
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/reset-password/', views.user_reset_password, name='user_reset_password'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    
    # Stock management
    path('stock/', views.stock_list, name='stock_list'),
    path('stock/create/', views.drug_create, name='drug_create'),
    path('stock/<int:drug_id>/edit/', views.drug_edit, name='drug_edit'),
    path('stock/<int:drug_id>/delete/', views.drug_delete, name='drug_delete'),
    
    # Sales management
    path('sales/', views.sales_list, name='sales_list'),
] 