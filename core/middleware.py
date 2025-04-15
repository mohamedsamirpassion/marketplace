from django.utils import translation
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
import threading

# Create a thread-local storage for language
_language = threading.local()

class CustomLocaleMiddleware(MiddlewareMixin):
    """
    Custom middleware for language selection that doesn't rely on .mo files
    """
    
    def process_request(self, request):
        # Get language from cookie
        language = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
        
        # If not in cookie, check if user has a language preference
        # First check if request.user exists and is authenticated
        if not language and hasattr(request, 'user') and request.user.is_authenticated and hasattr(request.user, 'language'):
            language = request.user.language
        
        # If still no language, use the default
        if not language:
            # Use a simplified approach without translation.get_language_from_request
            accept = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
            for lang_code, lang_name in settings.LANGUAGES:
                if lang_code in accept:
                    language = lang_code
                    break
            
            if not language:
                language = settings.LANGUAGE_CODE
        
        # Only set languages that are in our LANGUAGES setting
        if language and language in [code for code, name in settings.LANGUAGES]:
            # Store the language in request and thread-local
            request.LANGUAGE_CODE = language
            _language.code = language
            
            # We avoid calling translation.activate(language) which reads .mo files
            # Instead, we manually set attributes that templates and code will use
            
            # Set the Content-Language for response
            if not hasattr(request, '_language_processed'):
                request._language_processed = True
                
            # Add language info to request
            if language == 'ar':
                request.LANGUAGE_BIDI = True  # Right-to-left language
            else:
                request.LANGUAGE_BIDI = False
        else:
            # Default to English
            request.LANGUAGE_CODE = settings.LANGUAGE_CODE
            request.LANGUAGE_BIDI = False
            _language.code = settings.LANGUAGE_CODE
            
    def process_response(self, request, response):
        if 'Content-Language' not in response:
            # Get language from thread-local or default
            language = getattr(_language, 'code', settings.LANGUAGE_CODE)
            response['Content-Language'] = language
        return response 