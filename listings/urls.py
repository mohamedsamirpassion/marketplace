from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('listing/<int:pk>/', views.listing_detail, name='listing_detail'),
    path('create/', views.create_listing, name='create_listing'),
    path('get-models/', views.get_models, name='get_models'),
    path('debug-models/', views.debug_models, name='debug_models'),
    path('submit-brand/', views.submit_brand, name='submit_brand'),
    path('submit-model/', views.submit_model, name='submit_model'),
    path('listing/<int:pk>/mark-as-sold/', views.mark_as_sold, name='mark_as_sold'),
    path('listing/<int:pk>/report/', views.report_listing, name='report_listing'),
    path('listing/<int:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.favorites_list, name='favorites_list'),
]