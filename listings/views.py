from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import CarListing
from .forms import CarListingForm, CarImageFormSet

def home(request):
    listings = CarListing.objects.filter(status='approved')
    return render(request, 'listings/home.html', {'listings': listings})
def listing_detail(request, pk):
    listing = CarListing.objects.get(pk=pk, status='approved')
    return render(request, 'listings/listing_detail.html', {'listing': listing})

@login_required
def create_listing(request):
    if request.method == 'POST':
        form = CarListingForm(request.POST)
        image_formset = CarImageFormSet(request.POST, request.FILES)
        if form.is_valid() and image_formset.is_valid():
            listing = form.save(commit=False)
            listing.seller = request.user
            listing.save()
            image_formset.instance = listing
            image_formset.save()
            return redirect('home')
    else:
        form = CarListingForm()
        image_formset = CarImageFormSet()
    return render(request, 'listings/create_listing.html', {
        'form': form,
        'image_formset': image_formset
    })