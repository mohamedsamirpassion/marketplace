from django.urls import path
from . import views

urlpatterns = [
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('accounts/signup/', views.signup, name='signup'),
    path('accounts/verify/<uidb64>/<token>/', views.verify_email, name='verify_email'),
]