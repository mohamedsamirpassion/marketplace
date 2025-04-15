from django.shortcuts import render, redirect
from django.utils import translation
from django.urls import is_valid_path, translate_url
from django.http import HttpResponseRedirect
from django.conf import settings

# Create your views here.

def set_language(request):
    """
    Custom language switcher that doesn't require compiled .mo files
    """
    next_url = request.POST.get('next', request.GET.get('next', '/'))
    response = HttpResponseRedirect(next_url)
    
    lang_code = request.POST.get('language', None)
    if lang_code and lang_code in [code for code, name in settings.LANGUAGES]:
        if request.user.is_authenticated and hasattr(request.user, 'language'):
            # If user is logged in, we can store their language preference
            request.user.language = lang_code
            request.user.save()
            
        # Set the language cookie
        response.set_cookie(
            settings.LANGUAGE_COOKIE_NAME,
            lang_code,
            max_age=settings.LANGUAGE_COOKIE_AGE,
            path=settings.LANGUAGE_COOKIE_PATH,
            domain=settings.LANGUAGE_COOKIE_DOMAIN,
            secure=settings.LANGUAGE_COOKIE_SECURE,
            httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
            samesite=settings.LANGUAGE_COOKIE_SAMESITE,
        )
        
        # Instead of using translation.activate which reads .mo files,
        # we just set the cookie and let the middleware handle it
        # Avoid: translation.activate(lang_code)
        
        # Still set the Content-Language header
        response.headers['Content-Language'] = lang_code
        
    return response
