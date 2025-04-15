from django.contrib.auth import get_user_model

User = get_user_model()

def refresh_user(request):
    """
    Utility function to refresh the user instance in the request with
    the latest data from the database.
    """
    if request.user.is_authenticated:
        fresh_user = User.objects.get(id=request.user.id)
        request.user = fresh_user
        return fresh_user
    return None 