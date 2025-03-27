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
        print("POST data:", request.POST)
        print("FILES data:", request.FILES)
        form = ListingForm(request.POST)
        image_formset = ListingImageFormSet(request.POST, request.FILES)
        if form.is_valid():
            print("Listing form is valid")
            if image_formset.is_valid():
                print("Image formset is valid")
                listing = form.save(commit=False)
                listing.seller = request.user
                listing.approved = False
                listing.save()
                for image_form in image_formset:
                    image = image_form.cleaned_data.get('image')
                    if image:
                        print(f"Saving image: {image}")
                        ListingImage.objects.create(listing=listing, image=image)
                    else:
                        print("No image in form:", image_form.cleaned_data)
                messages.success(request, "Your listing has been submitted successfully! One of our admins will review and approve it soon.")
                return redirect('home')
            else:
                print("Image formset errors:", image_formset.errors)
                messages.error(request, "Please correct the image upload errors below.")
        else:
            print("Listing form errors:", form.errors)
            messages.error(request, "Please correct the form errors below.")
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