from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from .models import User

class UserAdmin(BaseUserAdmin):
    list_display = ('name', 'email', 'phone_number', 'is_active', 'is_staff', 'is_verified', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_verified')
    search_fields = ('name', 'email', 'phone_number')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'phone_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
        ('Verification', {'fields': ('is_verified',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone_number', 'name', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )
    
    readonly_fields = ('last_login', 'date_joined')  # Mark as read-only
    
    actions = ['suspend_users', 'activate_users', 'reset_passwords']

    def suspend_users(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, "Selected users have been suspended.")
    suspend_users.short_description = "Suspend selected users"

    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, "Selected users have been activated.")
    activate_users.short_description = "Activate selected users"

    def reset_passwords(self, request, queryset):
        for user in queryset:
            # Generate a temporary password
            temp_password = get_random_string(length=12)  # Generate a 12-character random password
            user.set_password(temp_password)
            user.save()
            # Send email with temporary password
            subject = "Your Cairo Bazaar Password Has Been Reset"
            message = f"""
            Hello {user.name},

            An admin has reset your password. Your temporary password is:

            {temp_password}

            Please log in and change your password immediately at: http://{request.get_host()}/edit-profile/

            Thanks,
            The Cairo Bazaar Team
            """
            send_mail(subject, message, 'noreply@cairobazaar.com', [user.email])
        self.message_user(request, "Selected users' passwords have been reset and emails sent.")
    reset_passwords.short_description = "Reset passwords for selected users"
    
admin.site.register(User, UserAdmin)