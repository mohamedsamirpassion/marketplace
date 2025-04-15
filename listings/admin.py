from django.contrib import admin
from django import forms
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.safestring import mark_safe
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path, reverse
from django.utils import timezone
from django.db.models import Count
from .models import Brand, Model, PendingBrand, PendingModel, Listing, ListingImage, AdSpace, ListingReport, Favorite

class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_ar', 'approved', 'view_listings_button')
    list_filter = ('approved',)
    search_fields = ('name', 'name_ar')
    actions = ['approve_brands']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'approved')
        }),
        ('Arabic Translation', {
            'fields': ('name_ar',),
        }),
    )

    def approve_brands(self, request, queryset):
        queryset.update(approved=True)
        self.message_user(request, "Selected brands have been approved.")
    approve_brands.short_description = "Approve selected brands"
    
    def view_listings_button(self, obj):
        """Button to view all listings for this brand"""
        url = f"/admin/listings/listing/?brand__id__exact={obj.id}"
        return mark_safe(f'<a href="{url}" class="view-link">View Listings</a>')
    view_listings_button.short_description = "Listings"

class ModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_ar', 'brand', 'approved', 'view_listings_button')
    list_filter = ('approved', 'brand')
    search_fields = ('name', 'name_ar', 'brand__name', 'brand__name_ar')
    actions = ['approve_models']
    
    fieldsets = (
        (None, {
            'fields': ('brand', 'name', 'approved')
        }),
        ('Arabic Translation', {
            'fields': ('name_ar',),
        }),
    )

    def approve_models(self, request, queryset):
        queryset.update(approved=True)
        self.message_user(request, "Selected models have been approved.")
    approve_models.short_description = "Approve selected models"
    
    def view_listings_button(self, obj):
        """Button to view all listings for this model"""
        url = f"/admin/listings/listing/?model__id__exact={obj.id}"
        return mark_safe(f'<a href="{url}" class="view-link">View Listings</a>')
    view_listings_button.short_description = "Listings"

@admin.register(PendingBrand)
class PendingBrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'submitted_by', 'submitted_at')
    search_fields = ('name', 'submitted_by__email')
    list_filter = ('submitted_at',)
    actions = ['approve_brands', 'reject_brands']
    
    def approve_brands(self, request, queryset):
        for pending_brand in queryset:
            # Check if brand already exists
            if not Brand.objects.filter(name=pending_brand.name).exists():
                # Create a new brand
                Brand.objects.create(
                    name=pending_brand.name,
                    approved=True
                )
            # Delete the pending brand
            pending_brand.delete()
        self.message_user(request, f"{queryset.count()} brand(s) approved successfully.")
    approve_brands.short_description = "Approve selected brands"
    
    def reject_brands(self, request, queryset):
        queryset.delete()
        self.message_user(request, f"{queryset.count()} brand(s) rejected and removed.")
    reject_brands.short_description = "Reject selected brands"

@admin.register(PendingModel)
class PendingModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'submitted_by', 'submitted_at')
    search_fields = ('name', 'brand__name', 'submitted_by__email')
    list_filter = ('submitted_at', 'brand')
    actions = ['approve_models', 'reject_models']
    
    def approve_models(self, request, queryset):
        for pending_model in queryset:
            # Check if model already exists for this brand
            if not Model.objects.filter(name=pending_model.name, brand=pending_model.brand).exists():
                # Create a new model
                Model.objects.create(
                    name=pending_model.name,
                    brand=pending_model.brand,
                    approved=True
                )
            # Delete the pending model
            pending_model.delete()
        self.message_user(request, f"{queryset.count()} model(s) approved successfully.")
    approve_models.short_description = "Approve selected models"
    
    def reject_models(self, request, queryset):
        queryset.delete()
        self.message_user(request, f"{queryset.count()} model(s) rejected and removed.")
    reject_models.short_description = "Reject selected models"

class RejectionForm(forms.Form):
    rejection_reason = forms.CharField(widget=forms.Textarea, label="Reason for Rejection")

class ListingAdmin(admin.ModelAdmin):
    list_display = ('title_with_view_link', 'seller', 'formatted_price', 'approval_status', 'date_posted', 'sold_status', 'report_status', 'view_on_site_button')
    list_filter = ('approved', 'brand', 'model', 'is_sold', 'has_multiple_reports')
    search_fields = ('brand__name', 'model__name', 'seller__name')
    actions = ['approve_listings', 'reject_listings']
    
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        # Enable actions on the listing change form
        self.actions_on_top = True
        self.actions_on_bottom = True
        self.actions_selection_counter = True
    
    def approve_listings(self, request, queryset):
        count = queryset.update(approved=True)
        
        # If only one listing was approved and it's from the change form, redirect to view the listing
        if count == 1 and '_selected_action' in request.POST and len(request.POST.getlist('_selected_action')) == 1:
            listing_id = request.POST.getlist('_selected_action')[0]
            self.message_user(request, "Listing has been approved successfully.")
            
            # Check if there's a return URL in the request
            return_url = request.POST.get('return_url')
            if return_url and '/listing/' in return_url:
                return redirect(return_url)
                
            # Check if the request came from a form in the listing detail page
            elif 'HTTP_REFERER' in request.META and '/listing/' in request.META['HTTP_REFERER']:
                return redirect(f'/listing/{listing_id}/')
                
        else:
            self.message_user(request, f"{count} listings have been approved successfully.")
    approve_listings.short_description = "Approve selected listings"

    def title_with_view_link(self, obj):
        title = f"{obj.brand.name} {obj.model.name} ({obj.year})"
        
        # Add badge for listing status
        status_badge = ""
        if not obj.approved:
            status_badge = '<span class="status-badge status-pending">Pending</span> '
        elif obj.is_sold:
            status_badge = '<span class="status-badge status-sold">Sold</span> '
        
        return mark_safe(f"{status_badge}{title}")
    title_with_view_link.short_description = 'Listing'
    title_with_view_link.admin_order_field = 'brand__name'

    def formatted_price(self, obj):
        return f"{obj.price:,} EGP"
    formatted_price.short_description = 'Price'
    formatted_price.admin_order_field = 'price'

    def approval_status(self, obj):
        if obj.approved:
            return mark_safe('<span class="status-indicator status-approved"></span>Approved')
        else:
            return mark_safe('<span class="status-indicator status-pending"></span>Pending')
    approval_status.short_description = 'Status'
    approval_status.admin_order_field = 'approved'

    def sold_status(self, obj):
        if obj.is_sold:
            sold_date = obj.sold_date.strftime('%d %b %Y') if obj.sold_date else ''
            return mark_safe(f'<span class="status-indicator status-sold"></span>Sold{" on " + sold_date if sold_date else ""}')
        return ''
    sold_status.short_description = 'Sold'
    sold_status.admin_order_field = 'is_sold'

    def view_on_site_button(self, obj):
        view_url = f"/listing/{obj.id}/"
        css_class = "view-link"
        button_text = "View"
        
        # For unapproved listings, add a special class and text to indicate they're in preview mode
        if not obj.approved:
            css_class += " view-link-preview"
            button_text = "Preview"
            
        return mark_safe(f'<a href="{view_url}" class="{css_class}" target="_blank"><i class="fas fa-external-link-alt"></i> {button_text}</a>')
    view_on_site_button.short_description = 'View'

    def reject_listings(self, request, queryset):
        if request.POST.get('post'):
            form = RejectionForm(request.POST)
            if form.is_valid():
                rejection_reason = form.cleaned_data['rejection_reason']
                for listing in queryset:
                    listing.rejection_reason = rejection_reason
                    listing.save()
                    # Debug: Check seller email
                    print(f"Attempting to send email to seller: {listing.seller.email}")
                    if not listing.seller.email:
                        print(f"Warning: Seller email is empty for listing {listing}")
                        self.message_user(request, f"Warning: No email address for seller of listing {listing}", level='warning')
                        continue
                    try:
                        send_mail(
                            subject='Your Listing Has Been Rejected',
                            message=f'Your listing "{listing}" has been rejected for the following reason:\n\n{rejection_reason}\n\nPlease revise and resubmit if necessary.',
                            from_email=None,  # Uses DEFAULT_FROM_EMAIL from settings
                            recipient_list=[listing.seller.email],
                            fail_silently=False,
                        )
                        print(f"Email sent successfully to {listing.seller.email}")
                    except Exception as e:
                        print(f"Failed to send email to {listing.seller.email}: {str(e)}")
                        self.message_user(request, f"Failed to send email to {listing.seller.email}: {str(e)}", level='error')
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

    def report_status(self, obj):
        if obj.has_multiple_reports:
            return mark_safe('<span style="color: red; font-weight: bold;">⚠️ Multiple Reports</span>')
        
        # Check if there are any reports
        report_count = obj.reports.count()
        if report_count > 0:
            return mark_safe(f'<span style="color: orange;">📋 {report_count} Report(s)</span>')
        return '-'
    report_status.short_description = 'Reports'

    # Enable the "View on site" button in the admin interface
    def view_on_site(self, obj):
        return f"/listing/{obj.pk}/"

class AdSpaceAdmin(admin.ModelAdmin):
    list_display = ('location_on_page', 'is_active')
    list_filter = ('location_on_page', 'is_active')

@admin.register(ListingReport)
class ListingReportAdmin(admin.ModelAdmin):
    list_display = ('listing_link', 'reporter_link', 'reason_display', 'status', 'reported_on', 'action_buttons')
    list_filter = ('status', 'reason', 'reported_on')
    search_fields = ('listing__brand__name', 'listing__model__name', 'reporter__email', 'comment')
    readonly_fields = ('listing', 'reporter', 'reason', 'comment', 'reported_on')
    
    fieldsets = (
        ('Report Information', {
            'fields': ('listing', 'reporter', 'reason', 'comment', 'reported_on')
        }),
        ('Admin Actions', {
            'fields': ('status', 'admin_note', 'resolved_on')
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Only superusers can delete reports
        return request.user.is_superuser
    
    def listing_link(self, obj):
        url = f"/admin/listings/listing/{obj.listing.id}/change/"
        view_url = f"/listing/{obj.listing.id}/"
        return mark_safe(f'<a href="{url}">{obj.listing}</a> (<a href="{view_url}" target="_blank">View</a>)')
    listing_link.short_description = 'Listing'
    
    def reporter_link(self, obj):
        if obj.reporter:
            url = f"/admin/auth/user/{obj.reporter.id}/change/"
            return mark_safe(f'<a href="{url}">{obj.reporter.email}</a>')
        return "Unknown"
    reporter_link.short_description = 'Reporter'
    
    def reason_display(self, obj):
        return obj.get_reason_display()
    reason_display.short_description = 'Reason'
    
    def action_buttons(self, obj):
        if obj.status == 'pending':
            return mark_safe(
                f'<a class="button" href="/admin/listings/listingreport/{obj.id}/resolve/">Resolve</a> '
                f'<a class="button" href="/admin/listings/listingreport/{obj.id}/dismiss/">Dismiss</a>'
            )
        return '-'
    action_buttons.short_description = 'Actions'
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<int:report_id>/resolve/', self.admin_site.admin_view(self.resolve_report), name='resolve_report'),
            path('<int:report_id>/dismiss/', self.admin_site.admin_view(self.dismiss_report), name='dismiss_report'),
        ]
        return custom_urls + urls
    
    def resolve_report(self, request, report_id):
        report = get_object_or_404(ListingReport, id=report_id)
        if request.method == 'POST':
            admin_note = request.POST.get('admin_note', '')
            report.resolve(admin_note)
            self.message_user(request, f"Report on {report.listing} has been resolved.")
            return redirect('admin:listings_listingreport_changelist')
        
        return render(request, 'admin/report_action.html', {
            'report': report,
            'action': 'resolve',
            'title': f"Resolve report on {report.listing}",
            'opts': self.model._meta,
        })
    
    def dismiss_report(self, request, report_id):
        report = get_object_or_404(ListingReport, id=report_id)
        if request.method == 'POST':
            admin_note = request.POST.get('admin_note', '')
            report.dismiss(admin_note)
            self.message_user(request, f"Report on {report.listing} has been dismissed.")
            return redirect('admin:listings_listingreport_changelist')
        
        return render(request, 'admin/report_action.html', {
            'report': report,
            'action': 'dismiss',
            'title': f"Dismiss report on {report.listing}",
            'opts': self.model._meta,
        })

# Add custom admin view for report dashboard
@staff_member_required
def report_dashboard(request):
    # Get reports by status
    pending_reports = ListingReport.objects.filter(status='pending')
    resolved_reports = ListingReport.objects.filter(status='resolved')
    dismissed_reports = ListingReport.objects.filter(status='dismissed')
    
    # Get reports by reason
    reports_by_reason = ListingReport.objects.values('reason').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Get listings with multiple reports
    flagged_listings = Listing.objects.filter(has_multiple_reports=True, approved=True)
    
    # Get recent reports
    recent_reports = ListingReport.objects.order_by('-reported_on')[:10]
    
    # Context data
    context = {
        'title': 'Report Dashboard',
        'pending_count': pending_reports.count(),
        'resolved_count': resolved_reports.count(),
        'dismissed_count': dismissed_reports.count(),
        'reports_by_reason': reports_by_reason,
        'report_reasons': ListingReport.REPORT_REASONS,  # Add the report reasons choices
        'flagged_listings': flagged_listings,
        'recent_reports': recent_reports,
        'site_header': admin.site.site_header,
        'site_title': admin.site.site_title,
    }
    
    return render(request, 'admin/report_dashboard.html', context)

# Register the view through an admin.py URL pattern instead
# This approach doesn't require modifying the AdminSite class

class ListingsAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('reports/', self.admin_view(report_dashboard), name='report_dashboard'),
        ]
        return custom_urls + urls

# Don't replace the default admin site, just add the URL pattern
# We'll register this view in urls.py instead

admin.site.register(Brand, BrandAdmin)
admin.site.register(Model, ModelAdmin)
admin.site.register(Listing, ListingAdmin)
admin.site.register(ListingImage)
admin.site.register(AdSpace, AdSpaceAdmin)
admin.site.register(Favorite)

# Delete the previous attempt at adding a custom view
if hasattr(admin.site, '_registry') and 'Report Dashboard' in admin.site._registry:
    del admin.site._registry['Report Dashboard']

# Add a custom admin header with the report dashboard link
def listings_admin_context_processor(request):
    """Add extra context to admin pages"""
    if request.path.startswith('/admin/'):
        return {
            'report_dashboard_url': reverse('admin_report_dashboard'),
            'has_report_access': request.user.is_staff,
        }
    return {}

# Add this to your settings.py TEMPLATES context_processors
# 'listings.admin.listings_admin_context_processor',