from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from allauth.socialaccount.providers.google.views import oauth2_login

urlpatterns = [
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('direct-update-profile/', views.direct_update_profile, name='direct_update_profile'),
    path('accounts/signup/', views.signup, name='register'),
    path('accounts/verify/<uidb64>/<token>/', views.verify_email, name='verify_email'),
    path('profile/<int:pk>/', views.user_profile, name='user_profile'),
    
    # Authentication URLs
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    
    # Password reset URLs - Django default pattern
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(
        template_name='users/password_reset.html'), 
        name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='users/password_reset_done.html'), 
        name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='users/password_reset_confirm.html'), 
        name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='users/password_reset_complete.html'), 
        name='password_reset_complete'),
    
    # Allauth password reset URLs - same views but different URL patterns
    path('accounts/password/reset/', auth_views.PasswordResetView.as_view(
        template_name='users/password_reset.html'),
        name='account_reset_password'),
    path('accounts/password/reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='users/password_reset_done.html'),
        name='account_reset_password_done'),
    path('accounts/password/reset/key/<uidb36>-<key>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='users/password_reset_confirm.html'),
        name='account_reset_password_from_key'),
    path('accounts/password/reset/key/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='users/password_reset_complete.html'),
        name='account_reset_password_from_key_done'),
        
    path('accounts/google/login/', oauth2_login, name='google_login'),
]