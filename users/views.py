from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from .forms import SignUpForm
from .models import User

@login_required
def edit_profile(request):
    if request.method == 'POST':
        user = request.user
        user.name = request.POST['name']
        user.phone_number = request.POST['phone_number']
        # Handle password change
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        if new_password and confirm_password:
            if new_password == confirm_password:
                user.set_password(new_password)
            else:
                return render(request, 'users/edit_profile.html', {
                    'user': user,
                    'error': 'Passwords do not match.'
                })
        user.save()
        return redirect('home')
    return render(request, 'users/edit_profile.html', {'user': request.user})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate until verified
            user.save()
            # Send verification email
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            domain = request.get_host()
            link = f"http://{domain}/accounts/verify/{uid}/{token}/"
            subject = "Verify Your Marketplace Account"
            message = render_to_string('registration/verification_email.html', {
                'user': user,
                'link': link,
            })
            send_mail(subject, message, 'noreply@marketplace.com', [user.email])
            return render(request, 'registration/signup_done.html')
    else:
        form = SignUpForm()
    return render(request, 'users/signup.html', {'form': form})

def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.is_verified = True
            user.save()
            login(request, user)
            return redirect('home')
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        pass
    return render(request, 'registration/verification_failed.html')