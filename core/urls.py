from django.urls import path
from . import views

urlpatterns = [
    path('setlang/', views.set_language, name='set_language'),
] 