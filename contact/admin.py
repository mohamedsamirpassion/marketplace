from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.conf import settings
from .models import ContactMessage

class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'user_email', 'created_at', 'status')
    list_filter = ('status', 'created_at')
    search_fields = ('subject', 'message', 'user__email', 'admin_response')
    readonly_fields = ('user', 'subject', 'message', 'created_at')
    fieldsets = (
        (_('User Message'), {
            'fields': ('user', 'subject', 'message', 'created_at', 'status')
        }),
        (_('Admin Response'), {
            'fields': ('admin_notes', 'admin_response', 'responded_at')
        }),
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = _('User Email')
    
    def save_model(self, request, obj, form, change):
        # Check if admin_response field was changed and not empty
        if 'admin_response' in form.changed_data and obj.admin_response:
            # Update responded_at timestamp
            obj.responded_at = timezone.now()
            obj.status = 'resolved'
            
            # Send email notification to user
            subject = _('Response to your inquiry: {0}').format(obj.subject)
            message = _("""
Hello,

We have responded to your inquiry.

Your original message:
{0}

Our response:
{1}

Thank you for contacting us.
Cairo Bazaar Team
            """).format(obj.message, obj.admin_response)
            
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[obj.user.email],
                    fail_silently=False,
                )
            except Exception as e:
                # Just log the error, don't prevent saving
                print(f"Failed to send email: {e}")
                
        super().save_model(request, obj, form, change)

admin.site.register(ContactMessage, ContactMessageAdmin)
