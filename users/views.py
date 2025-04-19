from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.http import Http404
from django.contrib import messages
from .forms import SignUpForm, CustomUserChangeForm
from .models import User
from listings.models import Listing, AdSpace
import re
from django.conf import settings
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)

@login_required
def edit_profile(request):
    # Check if this is a social account user
    is_social_user = hasattr(request.user, 'socialaccount_set') and request.user.socialaccount_set.exists()
    
    if is_social_user:
        # For social users, keep the direct form processing
        if request.method == 'POST':
            try:
                user = request.user
                messages.info(request, 'Processing social account profile update')
                
                # Update user name
                original_name = user.name
                new_name = request.POST['name']
                user.name = new_name
                
                # Update country code and phone if provided
                if 'country_code' in request.POST:
                    user.country_code = request.POST['country_code']
                
                if 'phone' in request.POST and request.POST['phone'].strip():
                    # Clean phone number
                    phone_number = request.POST['phone']
                    phone_number = re.sub(r'\D', '', phone_number)
                    
                    # For Egypt numbers, handle the leading zero
                    if user.country_code == '+20' and phone_number.startswith('0'):
                        phone_number = phone_number[1:]
                        
                    # Check the length based on country code
                    if user.country_code == '+20' and len(phone_number) != 10:
                        messages.error(request, "Egyptian phone numbers should be 10 digits (or 9 digits if you exclude the leading zero).")
                        return render(request, 'users/edit_profile.html', {'user': user})
                        
                    user.phone_number = phone_number
                
                # Set WhatsApp flag
                user.has_whatsapp = 'has_whatsapp' in request.POST
                
                # Save the user
                user.save()
                
                messages.success(request, f'Your profile has been updated successfully. Name changed from "{original_name}" to "{user.name}"')
                
                # Redirect to profile
                return redirect('user_profile', pk=user.id)
                
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                messages.error(request, f'Error updating profile: {str(e)}')
                print(f"PROFILE UPDATE ERROR: {str(e)}\n{error_details}")
                return render(request, 'users/edit_profile.html', {'user': request.user})
                
        return render(request, 'users/edit_profile.html', {'user': request.user})
    
    else:
        # For regular users, use the CustomUserChangeForm
        if request.method == 'POST':
            form = CustomUserChangeForm(request.POST, instance=request.user)
            if form.is_valid():
                user = form.save(commit=False)
                
                # Handle password change if provided
                password = form.cleaned_data.get('password')
                if password:
                    user.set_password(password)
                    update_session_auth_hash(request, user)  # Keep user logged in
                
                user.save()
                messages.success(request, 'Your profile has been updated successfully.')
                return redirect('user_profile', pk=user.id)
            else:
                # If form is not valid, show errors
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
        else:
            # For GET requests, initialize the form with current user data
            form = CustomUserChangeForm(instance=request.user)
        
        return render(request, 'users/edit_profile.html', {'user': request.user, 'form': form})

@login_required
def direct_update_profile(request):
    """
    A simplified profile update for social users that bypasses validation 
    and directly updates the database. This ensures that even if there are issues
    with the standard edit_profile view, social users can still update their name.
    """
    if request.method == 'POST':
        try:
            # Get a direct reference to the user from the database
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user_id = request.user.id
            
            # Get the new name from the form
            new_name = request.POST.get('name', '').strip()
            
            if not new_name:
                messages.error(request, 'Name cannot be empty')
                return redirect('edit_profile')
            
            # Directly update the user in the database
            affected_rows = User.objects.filter(id=user_id).update(name=new_name)
            
            if affected_rows == 1:
                # Successfully updated, now reload the user
                updated_user = User.objects.get(id=user_id)
                
                # Force update the session
                request.user = updated_user
                request._cached_user = updated_user
                request.session['_auth_user_id'] = str(updated_user.pk)
                request.session.modified = True
                
                messages.success(request, f'Your name has been updated to: {new_name}')
                return redirect('user_profile', pk=user_id)
            else:
                messages.error(request, 'No changes were made. Please try again.')
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            messages.error(request, f'Error updating profile: {str(e)}')
            print(f"DIRECT PROFILE UPDATE ERROR: {str(e)}\n{error_details}")
            
    return redirect('edit_profile')

def user_profile(request, pk):
    profile_user = get_object_or_404(User, id=pk, is_active=True)
    
    # Check if viewing own profile
    is_own_profile = request.user.is_authenticated and request.user.id == profile_user.id
    
    # Get listings for this user
    active_listings = Listing.objects.filter(
        seller=profile_user, 
        approved=True, 
        is_sold=False
    ).order_by('-date_posted')
    
    sold_listings = Listing.objects.filter(
        seller=profile_user, 
        approved=True, 
        is_sold=True
    ).order_by('-sold_date')
    
    # Only show pending listings if viewing own profile
    pending_listings = []
    if is_own_profile:
        pending_listings = Listing.objects.filter(
            seller=profile_user, 
            approved=False
        ).order_by('-date_posted')
    
    # Get ads for display
    ad_spaces = AdSpace.objects.filter(is_active=True)
    
    context = {
        'profile_user': profile_user,
        'active_listings': active_listings,
        'sold_listings': sold_listings,
        'pending_listings': pending_listings,
        'is_own_profile': is_own_profile,
        'ad_spaces': ad_spaces,
    }
    
    return render(request, 'users/user_profile.html', context)

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # This block remains the same for *new* users
            try:
                user = form.save(commit=False)
                # Always activate the user immediately regardless of DEBUG setting
                user.is_active = True  # Changed: Always activate users
                user.is_verified = True  # Mark as verified to avoid verification issues
                user.country_code = form.cleaned_data['country_code']
                user.has_whatsapp = form.cleaned_data.get('has_whatsapp', False)
                user.save()
                
                # Generate verification token and URL
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                verification_url = request.build_absolute_uri(
                    reverse('verify_email', kwargs={'uidb64': uid, 'token': token})
                )
                
                # Still try to send verification email, but don't require it for activation
                try:
                    subject = 'Verify your Cairo Bazaar account'
                    message = render_to_string('users/verification_email.html', {
                        'user': user,
                        'verification_url': verification_url,
                    })
                    
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        html_message=message,
                        fail_silently=False,
                    )
                    
                    # Since user is already active, just inform them they can log in
                    messages.success(request, 'Account created successfully! You can now log in. We also sent a confirmation email.')
                    return redirect('login')
                    
                except Exception as e:
                    logger.error(f"Failed to send verification email: {str(e)}")
                    # User is already active, just inform them they can log in
                    messages.success(request, 'Account created successfully! You can now log in.')
                    return redirect('login')
                    
            except Exception as e:
                logger.error(f"Error during new user signup: {str(e)}")
                messages.error(request, 'An error occurred during signup. Please try again.')
                return redirect('signup')
        else:
            # Check if the error is specifically "email already exists"
            if 'email' in form.errors and any('already exists' in e for e in form.errors['email']):
                logger.info(f"Signup attempt for existing email: {request.POST.get('email')}")
                try:
                    # Try to find the existing, potentially inactive user
                    existing_user = User.objects.get(email=request.POST.get('email'))
                    if not existing_user.is_active:
                        # Found an inactive user - let's activate them
                        logger.info(f"Found inactive user {existing_user.email}. Activating.")
                        existing_user.is_active = True
                        existing_user.save()
                        # Optionally try resending verification or just tell them to log in
                        messages.success(request, 'Your account already existed and has now been activated. Please try logging in.')
                        return redirect('login')
                    else:
                        # User exists and is already active - show the original form error
                        messages.error(request, 'This email is already registered and active. Please log in.')
                except User.DoesNotExist:
                    # Should not happen if form validation caught it, but handle defensively
                    logger.error(f"Form validation failed for existing email, but user not found: {request.POST.get('email')}")
                    messages.error(request, 'An unexpected error occurred. Please try again.')
                except Exception as e:
                    logger.error(f"Error activating existing user {request.POST.get('email')}: {str(e)}")
                    messages.error(request, 'An error occurred while trying to reactivate your account.')

            # If it wasn't the email exists error, or activation failed, show original form errors
            # Re-render the form with validation errors
            return render(request, 'users/signup.html', {'form': form})

    else: # GET request
        form = SignUpForm()
    
    return render(request, 'users/signup.html', {'form': form})

def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        
        # Log verification attempt for debugging
        print(f"Verification attempt for user ID {uid}, token: {token}")
        
        # Check if user is already active
        if user.is_active:
            messages.info(request, "Your account is already verified. You can login now.")
            return redirect('login')
            
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.is_verified = True
            user.save()
            login(request, user)
            messages.success(request, "Your account has been verified successfully. Welcome to Cairo Bazaar!")
            return redirect('home')
        else:
            print(f"Token validation failed for user {uid}")
            messages.error(request, "The verification link is invalid or has expired.")
    except (TypeError, ValueError, OverflowError) as e:
        print(f"Error decoding UID: {str(e)}")
        messages.error(request, "Invalid verification link.")
    except User.DoesNotExist:
        print(f"User with ID {uid} not found")
        messages.error(request, "User not found.")
    except Exception as e:
        print(f"Unexpected error during verification: {str(e)}")
        messages.error(request, "An unexpected error occurred during verification.")
    
    return render(request, 'registration/verification_failed.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember = request.POST.get('remember')
        
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            
            # Set session expiry if remember me is not checked
            if not remember:
                request.session.set_expiry(0)
                
            # Redirect to next page if available, otherwise home
            next_page = request.GET.get('next', 'home')
            return redirect(next_page)
        else:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'users/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')