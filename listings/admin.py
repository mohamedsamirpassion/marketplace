from django.contrib import admin
from .models import Brand, Model, PendingBrand, PendingModel, Listing, ListingImage

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

admin.site.register(Brand, BrandAdmin)
admin.site.register(Model, ModelAdmin)
admin.site.register(PendingBrand, PendingBrandAdmin)
admin.site.register(PendingModel, PendingModelAdmin)
admin.site.register(Listing)
admin.site.register(ListingImage)