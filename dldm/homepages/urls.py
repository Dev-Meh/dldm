from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('shop/', views.shop, name='shop'),
<<<<<<< HEAD
=======
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
>>>>>>> b87c717 (all project)
]

