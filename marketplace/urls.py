from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('django.contrib.auth.urls')),  # Add this line
    path('accounts/login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
]