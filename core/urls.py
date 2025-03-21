from django.urls import path
from .views import home, submit_ad, signup

urlpatterns = [
    path('', home, name='home'),
    path('ads/create/', submit_ad, name='submit_ad'),
    path('signup/', signup, name='signup'),  # Add this line
]