from django.urls import path
from .views import home, submit_ad

urlpatterns = [
    path('', home, name='home'),
    path('ads/create/', submit_ad, name='submit_ad'),
]