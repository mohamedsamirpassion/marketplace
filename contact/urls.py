from django.urls import path
from . import views

urlpatterns = [
    path('contact/', views.contact_us, name='contact_us'),
    path('contact/history/', views.contact_history, name='contact_history'),
    path('contact/detail/<int:pk>/', views.contact_detail, name='contact_detail'),
] 