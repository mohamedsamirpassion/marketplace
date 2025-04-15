from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .forms import ContactForm
from .models import ContactMessage

@login_required
def contact_us(request):
    """View for the contact form page"""
    if request.method == 'POST':
        form = ContactForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Your message has been sent successfully. We will get back to you soon.'))
            return redirect('contact_history')
    else:
        form = ContactForm(user=request.user)
    
    return render(request, 'contact/contact_form.html', {
        'form': form,
    })

@login_required
def contact_history(request):
    """View for users to see their contact history and admin responses"""
    user_messages = ContactMessage.objects.filter(user=request.user)
    
    return render(request, 'contact/contact_history.html', {
        'contact_messages': user_messages,
    })

@login_required
def contact_detail(request, pk):
    """View a specific contact message and its response"""
    message = ContactMessage.objects.get(pk=pk, user=request.user)
    
    return render(request, 'contact/contact_detail.html', {
        'message': message,
    })
