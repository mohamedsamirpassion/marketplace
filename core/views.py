from django.shortcuts import render, redirect
from django.utils import translation
from django.urls import is_valid_path, translate_url
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import os

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

def change_language(request, language_code):
    """
    Simple URL-based language changer for users who prefer a GET request approach
    """
    response = HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    
    if language_code and language_code in [code for code, name in settings.LANGUAGES]:
        if request.user.is_authenticated and hasattr(request.user, 'language'):
            # If user is logged in, we can store their language preference
            request.user.language = language_code
            request.user.save()
            
        # Set the language cookie
        response.set_cookie(
            settings.LANGUAGE_COOKIE_NAME,
            language_code,
            max_age=settings.LANGUAGE_COOKIE_AGE,
            path=settings.LANGUAGE_COOKIE_PATH,
            domain=settings.LANGUAGE_COOKIE_DOMAIN,
            secure=settings.LANGUAGE_COOKIE_SECURE,
            httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
            samesite=settings.LANGUAGE_COOKIE_SAMESITE,
        )
        
        # Set the Content-Language header
        response.headers['Content-Language'] = language_code
        
    return response

def cloudinary_test(request):
    """Test view to verify Cloudinary settings"""
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
    api_key = os.environ.get('CLOUDINARY_API_KEY')
    api_secret_masked = "***" if os.environ.get('CLOUDINARY_API_SECRET') else None
    
    # Return masked credentials (never expose full credentials)
    return JsonResponse({
        'cloudinary_configured': all([cloud_name, os.environ.get('CLOUDINARY_API_KEY'), os.environ.get('CLOUDINARY_API_SECRET')]),
        'cloud_name': cloud_name,
        'api_key_exists': bool(os.environ.get('CLOUDINARY_API_KEY')),
        'api_secret_exists': bool(os.environ.get('CLOUDINARY_API_SECRET')),
        'DEBUG': os.environ.get('DEBUG', 'Not set'),
    })

@csrf_exempt
def test_upload(request):
    """Test view with a form to upload an image to Cloudinary"""
    if request.method == 'POST' and request.FILES.get('image'):
        from cloudinary.uploader import upload
        from cloudinary.utils import cloudinary_url
        
        try:
            # Upload the image
            result = upload(request.FILES['image'])
            
            # Get the URL
            url, options = cloudinary_url(result['public_id'], format=result['format'])
            
            return render(request, 'core/test_upload.html', {
                'success': True,
                'url': url,
                'result': result
            })
        except Exception as e:
            return render(request, 'core/test_upload.html', {
                'success': False,
                'error': str(e)
            })
    
    return render(request, 'core/test_upload.html', {'success': None})
