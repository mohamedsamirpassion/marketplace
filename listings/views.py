from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import Listing, ListingImage, Model, AdSpace, Brand
from .forms import ListingForm, ListingImageFormSet

def home(request):
    listings = Listing.objects.filter(approved=True)
    ad_spaces = AdSpace.objects.filter(is_active=True)
    
    # Get filter parameters from the request
    brand_id = request.GET.get('brand')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    year = request.GET.get('year')
    condition = request.GET.get('condition')
    governorate = request.GET.get('governorate')
    sort = request.GET.get('sort')

    # Apply filters
    if brand_id:
        listings = listings.filter(brand_id=brand_id)
    if price_min:
        listings = listings.filter(price__gte=price_min)
    if price_max:
        listings = listings.filter(price__lte=price_max)
    if year:
        listings = listings.filter(year=year)
    if condition:
        listings = listings.filter(condition=condition)
    if governorate:
        if governorate == 'Greater Cairo':
            listings = listings.filter(governorate__in=['Cairo', 'Giza', 'Qalyubia'])
        else:
            listings = listings.filter(governorate=governorate)

    # Apply sorting
    if sort == 'lowest_price':
        listings = listings.order_by('price')
    elif sort == 'highest_price':
        listings = listings.order_by('-price')
    else:
        listings = listings.order_by('-date_posted')  # Default: Newly listed (descending)

    # Get all brands and governorates for the filter dropdowns
    brands = Brand.objects.filter(approved=True)
    # Get governorate choices from the governorate field
    governorates = [choice[0] for choice in Listing._meta.get_field('governorate').choices]
    governorates.insert(0, 'Greater Cairo')  # Add "Greater Cairo" as the first option

    context = {
        'listings': listings,
        'ad_spaces': ad_spaces,
        'brands': brands,
        'conditions': Listing._meta.get_field('condition').choices,
        'governorates': governorates,
    }
    return render(request, 'listings/home.html', context)

def listing_detail(request, pk):
    listing = Listing.objects.get(pk=pk)
    ad_spaces = AdSpace.objects.filter(is_active=True)
    print("Ad Spaces in Listing Detail:", list(ad_spaces))  # Debug output
    return render(request, 'listings/listing_detail.html', {'listing': listing, 'ad_spaces': ad_spaces})

@login_required
def create_listing(request):
    if request.method == 'POST':
        print("POST data:", request.POST)
        print("FILES data:", request.FILES)
        form = ListingForm(request.POST)
        if form.is_valid():
            print("Listing form is valid")
            listing = form.save(commit=False)
            listing.seller = request.user
            listing.approved = False
            listing.save()
            image_formset = ListingImageFormSet(request.POST, request.FILES, instance=listing)
            if image_formset.is_valid():
                print("Image formset is valid")
                image_formset.save()
                messages.success(request, "Your listing has been submitted successfully! One of our admins will review and approve it soon.")
                return redirect('home')
            else:
                print("Image formset errors:", image_formset.errors)
                messages.error(request, "Please correct the image upload errors below.")
                listing.delete()
        else:
            print("Listing form errors:", form.errors)
            messages.error(request, "Please correct the form errors below.")
            image_formset = ListingImageFormSet(request.POST, request.FILES)
    else:
        form = ListingForm()
        image_formset = ListingImageFormSet()
    return render(request, 'listings/create_listing.html', {'form': form, 'image_formset': image_formset})

def get_models(request):
    try:
        brand_id = request.GET.get('brand_id')
        if brand_id:
            brand_id = int(brand_id)
            models = Model.objects.filter(brand_id=brand_id, approved=True).values('id', 'name')
            return JsonResponse({'models': list(models)})
        return JsonResponse({'models': []})
    except (ValueError, TypeError) as e:
        return JsonResponse({'models': [], 'error': f'Invalid brand_id: {str(e)}'}, status=400)
    except Exception as e:
        return JsonResponse({'models': [], 'error': f'Server error: {str(e)}'}, status=500)