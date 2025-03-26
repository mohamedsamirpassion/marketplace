from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)

class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
            logger.debug(f"User: {user.email}, Staff: {user.is_staff}, Super: {user.is_superuser}, Verified: {user.is_verified}, Active: {user.is_active}")
            if user.check_password(password) and user.is_verified and user.is_active:
                return user
            else:
                logger.debug(f"Login failed: Password={user.check_password(password)}, Verified={user.is_verified}, Active={user.is_active}")
        except User.DoesNotExist:
            logger.debug(f"No user found for email: {email}")
        return None