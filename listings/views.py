from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import Listing, ListingImage, Brand, Model, PendingBrand, PendingModel
from .forms import ListingForm, ListingImageFormSet

def home(request):
    listings = Listing.objects.filter(approved=True)
    return render(request, 'listings/home.html', {'listings': listings})

def listing_detail(request, pk):
    listing = Listing.objects.get(pk=pk)
    return render(request, 'listings/listing_detail.html', {'listing': listing})

@login_required
def create_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST)
        image_formset = ListingImageFormSet(request.POST, request.FILES)
        if form.is_valid() and image_formset.is_valid():
            # Handle brand
            brand_data = form.cleaned_data['brand']
            new_brand = form.cleaned_data.get('new_brand')
            if str(brand_data) == 'other' and new_brand:
                brand, _ = Brand.objects.get_or_create(name=new_brand, approved=False)
                PendingBrand.objects.get_or_create(name=new_brand, submitted_by=request.user)
            else:
                brand = brand_data

            # Handle model
            model_data = form.cleaned_data['model']
            new_model = form.cleaned_data.get('new_model')
            if str(model_data) == 'other' and new_model:
                model, _ = Model.objects.get_or_create(brand=brand, name=new_model, approved=False)
                PendingModel.objects.get_or_create(brand=brand, name=new_model, submitted_by=request.user)
            else:
                model = model_data

            # Create listing
            listing = form.save(commit=False)
            listing.seller = request.user
            listing.brand = brand
            listing.model = model
            listing.approved = False
            listing.save()

            # Save images
            for image_form in image_formset:
                if image_form.cleaned_data.get('image'):
                    ListingImage.objects.create(listing=listing, image=image_form.cleaned_data['image'])

            messages.success(request, "Your listing has been submitted for admin approval.")
            return redirect('home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ListingForm()
        image_formset = ListingImageFormSet(queryset=ListingImage.objects.none())
    return render(request, 'listings/create_listing.html', {'form': form, 'image_formset': image_formset})

def get_models(request):
    brand_id = request.GET.get('brand_id')
    if brand_id and brand_id != 'other':
        models = Model.objects.filter(brand_id=brand_id, approved=True).values('id', 'name')
        return JsonResponse({'models': list(models)})
    return JsonResponse({'models': []})