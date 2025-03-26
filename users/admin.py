from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
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
    
    actions = ['suspend_users', 'activate_users']

    def suspend_users(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, "Selected users have been suspended.")
    suspend_users.short_description = "Suspend selected users"

    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, "Selected users have been activated.")
    activate_users.short_description = "Activate selected users"

admin.site.register(User, UserAdmin)