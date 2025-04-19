from django.urls import path
from . import views

urlpatterns = [
    path('setlang/', views.set_language, name='set_language'),
    path('change-language/<str:language_code>/', views.change_language, name='change_language'),
    path('cloudinary-test/', views.cloudinary_test, name='cloudinary_test'),
    path('test-upload/', views.test_upload, name='test_upload'),
] 