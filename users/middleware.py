from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin

User = get_user_model()

class RefreshUserMiddleware(MiddlewareMixin):
    """
    Middleware that refreshes the user instance in the request on every request.
    This ensures that template context always has the most up-to-date user data.
    """
    def process_request(self, request):
        if hasattr(request, 'user') and request.user.is_authenticated:
            try:
                # Get fresh user data from database
                fresh_user = User.objects.get(pk=request.user.pk)
                # Update the user in the request
                request.user = fresh_user
            except User.DoesNotExist:
                # User may have been deleted, handle gracefully
                pass
        return None 