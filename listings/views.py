from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import Listing, ListingImage, Model
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
            listing = form.save(commit=False)
            listing.seller = request.user
            listing.approved = False
            listing.save()
            for image_form in image_formset:
                if image_form.cleaned_data.get('image'):
                    ListingImage.objects.create(listing=listing, image=image_form.cleaned_data['image'])
            messages.success(request, "Your listing has been submitted successfully! One of our admins will review and approve it soon.")
            return redirect('home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ListingForm()
        image_formset = ListingImageFormSet(queryset=ListingImage.objects.none())
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