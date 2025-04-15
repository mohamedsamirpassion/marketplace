from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.contrib.auth import get_user_model
from allauth.account.utils import user_email, user_field, user_username
from allauth.utils import valid_email_or_none
from django.core.exceptions import MultipleObjectsReturned

User = get_user_model()

class CustomAccountAdapter(DefaultAccountAdapter):
    """Custom adapter for normal authentication handling"""
    def populate_username(self, request, user):
        """Override to prevent username population since we don't use it"""
        # Our User model doesn't have a username field, so we don't need to populate it
        return user
    
    def save_user(self, request, user, form, commit=True):
        """Override to save user without username field"""
        data = form.cleaned_data
        email = data.get('email')
        user.email = email or ''
        
        # Set name from the form if we have a 'name' field
        if 'name' in data:
            user.name = data['name']
        # Otherwise, use email as a fallback name
        elif not user.name and user.email:
            user.name = user.email.split('@')[0]
            
        if commit:
            user.save()
        return user
        
class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom adapter for social authentication handling"""
    def populate_user(self, request, sociallogin, data):
        """Populate user instance from social account data"""
        user = sociallogin.user
        
        # Get email from social account, verify it's valid
        email = valid_email_or_none(data.get('email'))
        if email:
            user.email = email
        
        # Get name from social account
        name = ""
        if sociallogin.account.provider == 'google':
            name = data.get('name', '')
        elif sociallogin.account.provider == 'facebook':
            name = data.get('name', '')
            
        # If no name is provided, use part of email
        if name:
            user.name = name
        elif not user.name and user.email:
            user.name = user.email.split('@')[0]
            
        return user
    
    def pre_social_login(self, request, sociallogin):
        """
        Called before the social login is attempted.
        Here we can intercept the login to prevent overriding user data.
        """
        # Check if the user already exists
        user = sociallogin.user
        email = user.email
        
        print(f"PRE SOCIAL LOGIN: Processing {email} with provider {sociallogin.account.provider}")
        
        try:
            # Check if user with this email already exists
            existing_user = User.objects.get(email=email)
            
            if existing_user:
                print(f"PRE SOCIAL LOGIN: Found existing user {existing_user.id} with name: {existing_user.name}")
                
                # Keep existing user's data instead of overwriting with social data
                sociallogin.user = existing_user
                
                # Only connect social account if not already connected
                if not hasattr(existing_user, 'socialaccount_set') or not existing_user.socialaccount_set.filter(provider=sociallogin.account.provider).exists():
                    print(f"PRE SOCIAL LOGIN: Connecting social account to existing user")
                    # The social account connection will happen later in the flow
                else:
                    print(f"PRE SOCIAL LOGIN: Social account already connected")
        
        except User.DoesNotExist:
            # User doesn't exist yet, let the normal flow continue
            print(f"PRE SOCIAL LOGIN: User does not exist yet, will create new user")
            pass
            
        return super().pre_social_login(request, sociallogin)
        
    def save_user(self, request, sociallogin, form=None):
        """Save the newly signed up social login"""
        user = sociallogin.user
        sociallogin.save(request)
        return user
    
    def update_user(self, user, sociallogin, data={}):
        """
        Override update_user to prevent updating the name from social data
        if the user already exists. This prevents Google from overwriting
        user's name changes.
        """
        # Update email if needed, since email verification status might change
        email = valid_email_or_none(data.get('email'))
        if email:
            user.email = email

        # Important: We NEVER update the name from social data for existing users
        # This ensures that if a user changes their name, it won't be overwritten
        # by future social logins
        
        # Only for brand new users (no ID yet), set the initial name
        if not user.id:
            name = data.get('name', '')
            if name:
                user.name = name
            elif not user.name and user.email:
                user.name = user.email.split('@')[0]

        # Print debug info to console
        if user.id:
            print(f"SOCIAL LOGIN: Preserving existing user name: {user.name}")
        else:
            print(f"SOCIAL LOGIN: New user, setting name: {user.name}")
            
        return user
        
    def get_app(self, request, provider, client_id=None):
        """
        Override the default get_app method to handle MultipleObjectsReturned gracefully.
        This method retrieves the SocialApp instance for the given provider/client_id.
        """
        from allauth.socialaccount.models import SocialApp
        
        # First, try to find by both provider and client_id if client_id is provided
        if client_id:
            try:
                return SocialApp.objects.get(provider=provider, client_id=client_id)
            except SocialApp.DoesNotExist:
                pass
            except MultipleObjectsReturned:
                print(f"WARNING: Multiple apps found for provider={provider}, client_id={client_id}. Using first.")
                return SocialApp.objects.filter(provider=provider, client_id=client_id).first()
        
        # Next, try with just provider
        try:
            return SocialApp.objects.get(provider=provider)
        except SocialApp.DoesNotExist:
            raise SocialApp.DoesNotExist(f"No SocialApp found for provider {provider}")
        except MultipleObjectsReturned:
            print(f"WARNING: Multiple apps found for provider={provider}. Using first.")
            return SocialApp.objects.filter(provider=provider).first()