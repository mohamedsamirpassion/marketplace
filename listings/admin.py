from django.contrib import admin
from django import forms
from django.core.mail import send_mail
from .models import Brand, Model, PendingBrand, PendingModel, Listing, ListingImage, AdSpace

class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'approved')
    list_filter = ('approved',)
    search_fields = ('name',)
    actions = ['approve_brands']

    def approve_brands(self, request, queryset):
        queryset.update(approved=True)
        self.message_user(request, "Selected brands have been approved.")
    approve_brands.short_description = "Approve selected brands"

class ModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'approved')
    list_filter = ('approved', 'brand')
    search_fields = ('name', 'brand__name')
    actions = ['approve_models']

    def approve_models(self, request, queryset):
        queryset.update(approved=True)
        self.message_user(request, "Selected models have been approved.")
    approve_models.short_description = "Approve selected models"

class PendingBrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'submitted_by', 'submitted_at')
    search_fields = ('name', 'submitted_by__name')
    actions = ['approve_pending_brands', 'reject_pending_brands']

    def approve_pending_brands(self, request, queryset):
        for pending_brand in queryset:
            Brand.objects.get_or_create(name=pending_brand.name, approved=True)
            pending_brand.delete()
        self.message_user(request, "Selected brands have been approved and added to the list.")
    approve_pending_brands.short_description = "Approve selected pending brands"

    def reject_pending_brands(self, request, queryset):
        queryset.delete()
        self.message_user(request, "Selected pending brands have been rejected.")
    reject_pending_brands.short_description = "Reject selected pending brands"

class PendingModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'submitted_by', 'submitted_at')
    search_fields = ('name', 'brand__name', 'submitted_by__name')
    actions = ['approve_pending_models', 'reject_pending_models']

    def approve_pending_models(self, request, queryset):
        for pending_model in queryset:
            Model.objects.get_or_create(brand=pending_model.brand, name=pending_model.name, approved=True)
            pending_model.delete()
        self.message_user(request, "Selected models have been approved and added to the list.")
    approve_pending_models.short_description = "Approve selected pending models"

    def reject_pending_models(self, request, queryset):
        queryset.delete()
        self.message_user(request, "Selected pending models have been rejected.")
    reject_pending_models.short_description = "Reject selected pending models"

class RejectionForm(forms.Form):
    rejection_reason = forms.CharField(widget=forms.Textarea, label="Reason for Rejection")

class ListingAdmin(admin.ModelAdmin):
    list_display = ('brand', 'model', 'year', 'seller', 'approved', 'date_posted', 'rejection_reason')
    list_filter = ('approved', 'brand', 'model')
    search_fields = ('brand__name', 'model__name', 'seller__name')
    actions = ['approve_listings', 'reject_listings']

    def approve_listings(self, request, queryset):
        queryset.update(approved=True)
        self.message_user(request, "Selected listings have been approved.")
    approve_listings.short_description = "Approve selected listings"

    def reject_listings(self, request, queryset):
        if request.POST.get('post'):
            form = RejectionForm(request.POST)
            if form.is_valid():
                rejection_reason = form.cleaned_data['rejection_reason']
                for listing in queryset:
                    listing.rejection_reason = rejection_reason
                    listing.save()
                    # Send email to the seller
                    send_mail(
                        subject='Your Listing Has Been Rejected',
                        message=f'Your listing "{listing}" has been rejected for the following reason:\n\n{rejection_reason}\n\nPlease revise and resubmit if necessary.',
                        from_email=None,  # Uses DEFAULT_FROM_EMAIL from settings
                        recipient_list=[listing.seller.email],
                        fail_silently=False,
                    )
                    listing.delete()
                self.message_user(request, f"Selected listings have been rejected with reason: {rejection_reason}")
                return
        else:
            form = RejectionForm()
            return self.get_action_form_response(request, queryset, form, "Reject Listings")
    reject_listings.short_description = "Reject selected listings"

    def get_action_form_response(self, request, queryset, form, action_title):
        from django.http import HttpResponse
        from django.template.response import TemplateResponse
        return TemplateResponse(request, 'admin/action_with_form.html', {
            'title': action_title,
            'objects': queryset,
            'form': form,
            'action': 'reject_listings',
        })

class AdSpaceAdmin(admin.ModelAdmin):
    list_display = ('location_on_page', 'is_active')
    list_filter = ('location_on_page', 'is_active')

admin.site.register(Brand, BrandAdmin)
admin.site.register(Model, ModelAdmin)
admin.site.register(PendingBrand, PendingBrandAdmin)
admin.site.register(PendingModel, PendingModelAdmin)
admin.site.register(Listing, ListingAdmin)
admin.site.register(ListingImage)
admin.site.register(AdSpace, AdSpaceAdmin)