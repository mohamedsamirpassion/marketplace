from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from listings.admin import report_dashboard
from django.contrib.admin.views.decorators import staff_member_required
from django.conf.urls.i18n import i18n_patterns

# URLs that don't need to be translated
urlpatterns = [
    # Replace Django's i18n URLs with our custom implementation
    # path('i18n/', include('django.conf.urls.i18n')),  # For language selection
    path('i18n/', include('core.urls')),  # Use our custom language selection
]

# Add non-i18n patterns that should still work without language prefix
urlpatterns += [
    path('', include('listings.urls')),  # Include all listings URLs at the root level too
]

# URLs that should be translated - all our main app URLs
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('admin/reports/', staff_member_required(report_dashboard), name='admin_report_dashboard'),
    path('', include('listings.urls')),
    # Use users.urls for all authentication paths, including password reset
    path('', include('users.urls')),
    path('accounts/', include('allauth.urls')),  # Place this after users.urls so our custom views take precedence
    path('', include('contact.urls')),  # Include contact app URLs
    prefix_default_language=False,  # Don't show /en/ prefix for default language
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)