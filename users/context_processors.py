from django.contrib.auth import get_user_model

User = get_user_model()

def current_user_processor(request):
    """
    Context processor that ensures the most up-to-date user data is available in templates.
    """
    if request.user.is_authenticated:
        # Get a fresh instance of the user to ensure all fields are up to date
        current_user = User.objects.get(id=request.user.id)
        return {'current_user': current_user}
    return {'current_user': None} 