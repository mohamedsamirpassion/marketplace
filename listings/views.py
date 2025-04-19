from django.shortcuts import render, redirect, get_object_or_404  # Add get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Listing, ListingImage, Model, AdSpace, Brand, PendingBrand, PendingModel, ListingReport, Favorite
from .forms import ListingForm, ListingImageFormSet, PendingBrandForm, PendingModelForm
import logging

logger = logging.getLogger(__name__)

def home(request):
    listings = Listing.objects.filter(approved=True, is_sold=False)
    ad_spaces = AdSpace.objects.filter(is_active=True)
    
    # Get filter parameters from the request
    brand_id = request.GET.get('brand')
    model_id = request.GET.get('model')  # Add model filter parameter
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    mileage_min = request.GET.get('mileage_min')
    mileage_max = request.GET.get('mileage_max')
    year = request.GET.get('year')
    condition = request.GET.get('condition')
    governorate = request.GET.get('governorate')
    transmission = request.GET.get('transmission')
    fuel_type = request.GET.get('fuel_type')
    sort = request.GET.get('sort')

    # Apply filters
    if brand_id:
        listings = listings.filter(brand_id=brand_id)
    if model_id:  # Add model filter
        listings = listings.filter(model_id=model_id)
    if price_min:
        listings = listings.filter(price__gte=price_min)
    if price_max:
        listings = listings.filter(price__lte=price_max)
    if mileage_min:
        listings = listings.filter(mileage__gte=mileage_min)
    if mileage_max:
        listings = listings.filter(mileage__lte=mileage_max)
    if year:
        listings = listings.filter(year=year)
    if condition:
        listings = listings.filter(condition=condition)
    if governorate:
        if governorate == 'Greater Cairo':
            listings = listings.filter(governorate__in=['Cairo', 'Giza', 'Qalyubia'])
        else:
            listings = listings.filter(governorate=governorate)
    if transmission:
        listings = listings.filter(transmission=transmission)
    if fuel_type:
        listings = listings.filter(fuel_type=fuel_type)

    # Apply sorting
    if sort == 'lowest_price':
        listings = listings.order_by('price')
    elif sort == 'highest_price':
        listings = listings.order_by('-price')
    elif sort == 'lowest_mileage':
        listings = listings.order_by('mileage')
    else:
        listings = listings.order_by('-date_posted')  # Default: Newly listed (descending)

    # Pagination
    paginator = Paginator(listings, 9)  # Show 9 listings per page
    page_number = request.GET.get('page')  # Get the current page number from the request
    page_obj = paginator.get_page(page_number)  # Get the listings for the current page

    # Get all brands and governorates for the filter dropdowns
    brands = Brand.objects.filter(approved=True).order_by('name')
    governorates = [choice[0] for choice in Listing._meta.get_field('governorate').choices]
    governorates.insert(0, 'Greater Cairo')  # Add "Greater Cairo" as the first option
    
    # Get models for the selected brand (if any)
    models = []
    if brand_id:
        models = Model.objects.filter(brand_id=brand_id, approved=True).order_by('name')

    # Get user's favorites for highlight
    favorited_listings = []
    if request.user.is_authenticated:
        favorited_listings = Favorite.objects.filter(user=request.user).values_list('listing_id', flat=True)
    
    context = {
        'listings': page_obj,
        'page_obj': page_obj,
        'ad_spaces': ad_spaces,
        'brands': brands,
        'models': models,  # Add models to context
        'conditions': Listing._meta.get_field('condition').choices,
        'governorates': governorates,
        'transmissions': Listing._meta.get_field('transmission').choices,
        'fuel_types': Listing._meta.get_field('fuel_type').choices,
        'selected_brand': brand_id,  # Pass selected brand to template
        'selected_model': model_id,  # Pass selected model to template
        'favorited_listings': favorited_listings,  # Pass user's favorited listings
    }
    return render(request, 'listings/home.html', context)

def listing_detail(request, pk):
    # For admins (staff users), allow viewing of all listings, including unapproved ones
    if request.user.is_staff:
        listing = get_object_or_404(Listing, pk=pk)  # Staff can view any listing
    else:
        listing = get_object_or_404(Listing, pk=pk, approved=True)  # Regular users can only see approved listings
    
    ad_spaces = AdSpace.objects.filter(is_active=True)
    
    # Check if the user is the owner of the listing
    is_owner = request.user.is_authenticated and request.user == listing.seller
    
    # Add a flag for admin context to show approval button if needed
    is_admin = request.user.is_staff
    
    # Check if the listing is in user's favorites
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(user=request.user, listing=listing).exists()
    
    # Generate WhatsApp link with listing info
    whatsapp_link = None
    if listing.seller.has_whatsapp:
        whatsapp_link = listing.seller.get_whatsapp_link(listing)
    
    context = {
        'listing': listing, 
        'ad_spaces': ad_spaces,
        'is_owner': is_owner,
        'is_admin': is_admin,
        'is_favorited': is_favorited,
        'whatsapp_link': whatsapp_link
    }
    
    return render(request, 'listings/listing_detail.html', context)

@login_required
def create_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        # Initialize image_formset here to ensure it's available even if main form fails
        image_formset = ListingImageFormSet(request.POST, request.FILES, prefix='images') 

        if form.is_valid(): # Check main form first
            # Don't save the main listing yet, wait until image formset is also valid
            listing = form.save(commit=False) 
            listing.seller = request.user
            listing.approved = False # Listings require approval

            if image_formset.is_valid(): # Now check image formset
                try: # Wrap saving of both listing and images in one block
                    listing.save() # Save main listing FIRST
                    image_formset.instance = listing # Ensure instance is set before saving formset
                    image_formset.save() # Save images (this should trigger S3 upload)
                    # If you have M2M fields on the main form, save them after instance save
                    # form.save_m2m() # Uncomment if needed for ListingForm
                    
                    messages.success(request, "Your listing has been submitted successfully! One of our admins will review and approve it soon.")
                    return redirect('home')
                except Exception as e:
                    # Log the FULL exception if saving fails
                    logger.error(f"Error saving listing or image formset: {e}", exc_info=True)
                    messages.error(request, f'There was an error saving your listing. Please try again. Error: {e}')
                    # We don't redirect here, we will fall through to re-render the form
                    # Keep listing instance so form can potentially use it if needed (though it might be partially saved)

            else:
                # Image formset is invalid
                logger.error(f"Image formset errors: {image_formset.errors}")
                logger.error(f"Image formset non-form errors: {image_formset.non_form_errors()}")
                messages.error(request, "Please correct the image upload errors below.")
                # Don't save the listing instance if images are invalid

        else: # Main form is invalid
            # We might still have image_formset data if user submitted images
            logger.error(f"Listing form errors: {form.errors}")
            messages.error(request, "Please correct the main form errors below.")

        # If we reach here, either form was invalid or image_formset was invalid, or save failed.
        # Re-render the form with errors, passing both forms back.
        return render(request, 'listings/create_listing.html', {'form': form, 'image_formset': image_formset})

    else: # GET request
        form = ListingForm()
        image_formset = ListingImageFormSet(prefix='images')
        return render(request, 'listings/create_listing.html', {'form': form, 'image_formset': image_formset})

def get_models(request):
    try:
        brand_id = request.GET.get('brand_id')
        print(f"get_models called with brand_id={brand_id}")
        
        if brand_id:
            brand_id = int(brand_id)
            print(f"Looking for models with brand_id={brand_id}")
            
            # Check if the brand exists
            brand_exists = Brand.objects.filter(id=brand_id).exists()
            if not brand_exists:
                print(f"Brand with id={brand_id} does not exist")
                return JsonResponse({'models': [], 'error': 'Brand not found'}, status=404)
            
            models = Model.objects.filter(brand_id=brand_id, approved=True).values('id', 'name').order_by('name')
            models_list = list(models)
            print(f"Found {len(models_list)} models: {models_list}")
            
            return JsonResponse({'models': models_list})
        
        print("No brand_id provided")
        return JsonResponse({'models': []})
    except (ValueError, TypeError) as e:
        print(f"Invalid brand_id: {str(e)}")
        return JsonResponse({'models': [], 'error': f'Invalid brand_id: {str(e)}'}, status=400)
    except Exception as e:
        print(f"Server error in get_models: {str(e)}")
        return JsonResponse({'models': [], 'error': f'Server error: {str(e)}'}, status=500)

# Add a debug view
def debug_models(request):
    """Debug view to check models for specific brands"""
    brands = Brand.objects.filter(approved=True).order_by('name')
    
    brand_id = request.GET.get('brand_id')
    brand_models = []
    selected_brand = None
    
    if brand_id:
        try:
            selected_brand = Brand.objects.get(id=brand_id)
            brand_models = Model.objects.filter(brand_id=brand_id, approved=True)
        except Brand.DoesNotExist:
            pass
    
    # Get BMW brand and its models specifically
    try:
        bmw = Brand.objects.get(name='BMW')
        bmw_id = str(bmw.id)  # Convert to string for JavaScript
        bmw_models = Model.objects.filter(brand=bmw, approved=True)
    except Brand.DoesNotExist:
        bmw = None
        bmw_id = ""
        bmw_models = []
    
    html = """
    <html>
    <head>
        <title>Models Debug</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1, h2 { color: #333; }
            ul { list-style-type: none; padding: 0; }
            li { margin: 5px 0; padding: 5px; background: #f5f5f5; }
            .container { margin: 20px 0; padding: 10px; border: 1px solid #ddd; }
        </style>
    </head>
    <body>
        <h1>Models Debug</h1>
        
        <div class="container">
            <h2>BMW Models</h2>"""
    
    # Add BMW details
    if bmw:
        html += f"""
            <p>BMW ID: {bmw.id}</p>
            <p>BMW approved: {bmw.approved}</p>
            <p>Count: {bmw_models.count()}</p>
            <ul>"""
        
        for model in bmw_models:
            html += f"""
                <li>ID: {model.id}, Name: {model.name}, Approved: {model.approved}</li>"""
        
        html += """
            </ul>"""
    else:
        html += """
            <p>BMW brand not found in database</p>"""
    
    html += """
        </div>
        
        <div class="container">
            <h2>All Brands</h2>"""
    
    html += f"""
            <p>Count: {brands.count()}</p>
            <ul>"""
    
    for brand in brands:
        html += f"""
                <li>ID: {brand.id}, Name: {brand.name}, Approved: {brand.approved}</li>"""
    
    html += """
            </ul>
        </div>
        
        <div class="container">
            <h2>Select Brand to View Models</h2>
            <form>
                <select name="brand_id" onchange="this.form.submit()">
                    <option value="">Choose a brand</option>"""
    
    for brand in brands:
        selected = "selected" if brand_id and int(brand_id) == brand.id else ""
        html += f"""
                    <option value="{brand.id}" {selected}>{brand.name}</option>"""
    
    html += """
                </select>
            </form>"""
    
    if selected_brand:
        html += f"""
            <h3>Models for {selected_brand.name}</h3>
            <p>Count: {brand_models.count()}</p>
            <ul>"""
        
        for model in brand_models:
            html += f"""
                <li>ID: {model.id}, Name: {model.name}, Approved: {model.approved}</li>"""
        
        html += """
            </ul>"""
    
    html += f"""
        </div>
        
        <div class="container">
            <h2>Test API Call</h2>
            <button onclick="testApiCall()">Test Get Models API</button>
            <div id="api-result" style="margin-top: 10px; padding: 10px; background: #f0f0f0;"></div>
            
            <script>
                function testApiCall() {{
                    const bmwId = "{bmw_id}";
                    if (!bmwId) {{
                        document.getElementById('api-result').innerText = 'BMW brand not found in database.';
                        return;
                    }}
                    
                    fetch('/get-models/?brand_id=' + bmwId)
                        .then(response => response.json())
                        .then(data => {{
                            document.getElementById('api-result').innerText = 
                                'API Response for BMW (ID: ' + bmwId + '):\\n' + 
                                JSON.stringify(data, null, 2);
                        }})
                        .catch(error => {{
                            document.getElementById('api-result').innerText = 
                                'Error: ' + error.message;
                        }});
                }}
            </script>
        </div>
    </body>
    </html>
    """
    
    return HttpResponse(html)

@login_required
def submit_brand(request):
    if request.method == 'POST':
        form = PendingBrandForm(request.POST)
        if form.is_valid():
            pending_brand = form.save(commit=False)
            pending_brand.submitted_by = request.user
            pending_brand.save()
            messages.success(request, "Your brand suggestion has been submitted for approval.")
            
            # If this was called from an ajax request, return success response
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Brand suggestion submitted for approval.'})
            
            # Otherwise redirect to the previous page or home
            return redirect(request.META.get('HTTP_REFERER', 'home'))
        else:
            # If ajax request, return the errors
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
            
            messages.error(request, "Please correct the errors below.")
    else:
        form = PendingBrandForm()
    
    # Only render the full page for non-ajax requests
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'message': 'Invalid request method.'})
    
    return render(request, 'listings/submit_brand.html', {'form': form})

@login_required
def submit_model(request):
    if request.method == 'POST':
        form = PendingModelForm(request.POST)
        if form.is_valid():
            pending_model = form.save(commit=False)
            pending_model.submitted_by = request.user
            pending_model.save()
            messages.success(request, "Your model suggestion has been submitted for approval.")
            
            # If this was called from an ajax request, return success response
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Model suggestion submitted for approval.'})
            
            # Otherwise redirect to the previous page or home
            return redirect(request.META.get('HTTP_REFERER', 'home'))
        else:
            # If ajax request, return the errors
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
            
            messages.error(request, "Please correct the errors below.")
    else:
        brand_id = request.GET.get('brand_id')
        initial = {}
        if brand_id:
            try:
                brand = Brand.objects.get(id=brand_id, approved=True)
                initial = {'brand': brand}
            except Brand.DoesNotExist:
                pass
        form = PendingModelForm(initial=initial)
    
    # Only render the full page for non-ajax requests
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'message': 'Invalid request method.'})
    
    return render(request, 'listings/submit_model.html', {'form': form})

@login_required
def mark_as_sold(request, pk):
    """Mark a listing as sold or unsold"""
    listing = get_object_or_404(Listing, pk=pk)
    
    # Check if the user is the owner of the listing
    if request.user != listing.seller:
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('listing_detail', pk=pk)
    
    # Toggle the sold status
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'mark_sold':
            listing.is_sold = True
            listing.sold_date = timezone.now()
            messages.success(request, "Listing has been marked as sold!")
        elif action == 'mark_unsold':
            listing.is_sold = False
            listing.sold_date = None
            messages.success(request, "Listing has been marked as available!")
        
        listing.save()
        
        # Redirect back to referring page or user profile
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        return redirect('user_profile', user_id=request.user.id)
    
    # If not POST, redirect to listing detail
    return redirect('listing_detail', pk=pk)

@login_required
def report_listing(request, pk):
    """Handle reporting a listing for review by admins"""
    listing = get_object_or_404(Listing, pk=pk, approved=True)
    
    if request.method == 'POST':
        reason = request.POST.get('reason')
        comment = request.POST.get('comment', '')
        
        # Validate the reason is one of the valid choices
        valid_reasons = [choice[0] for choice in ListingReport.REPORT_REASONS]
        if reason not in valid_reasons:
            messages.error(request, 'Please select a valid reason for reporting this listing.')
            return redirect('listing_detail', pk=listing.pk)
        
        # Check if user already reported this listing
        existing_report = ListingReport.objects.filter(
            listing=listing,
            reporter=request.user,
            status='pending'
        ).exists()
        
        if existing_report:
            messages.info(request, 'You have already reported this listing. It is under review.')
        else:
            # Create the report
            report = ListingReport(
                listing=listing,
                reporter=request.user,
                reason=reason,
                comment=comment
            )
            report.save()
            
            # Send notification email to admins
            notify_admins_about_report(report)
            
            # Check if listing has multiple reports and flag it
            check_multiple_reports(listing)
            
            messages.success(request, 'Thank you for your report. Our team will review it.')
        
        return redirect('listing_detail', pk=listing.pk)
    
    # GET request shouldn't reach here, but just in case
    return redirect('listing_detail', pk=listing.pk)

def notify_admins_about_report(report):
    """Send email notification to site admins about new report"""
    from django.conf import settings
    from django.core.mail import mail_admins
    from django.urls import reverse
    
    admin_url = f"/admin/listings/listingreport/{report.id}/change/"
    listing_url = f"/listing/{report.listing.id}/"
    
    subject = f"New listing report: {report.get_reason_display()} - {report.listing}"
    
    message = f"""
A new listing has been reported:

Listing: {report.listing} 
Reporter: {report.reporter.email if report.reporter else 'Unknown'}
Reason: {report.get_reason_display()}
Date: {report.reported_on}

Comment:
{report.comment or "No comment provided"}

View this report in admin: {settings.SITE_URL}{admin_url}
View the listing: {settings.SITE_URL}{listing_url}
"""
    
    try:
        mail_admins(subject, message, fail_silently=False)
    except Exception as e:
        print(f"Failed to send admin notification email: {e}")

def check_multiple_reports(listing):
    """Check if listing has multiple reports and flag if needed"""
    # Count the number of distinct reporters for this listing
    report_count = ListingReport.objects.filter(
        listing=listing
    ).values('reporter').distinct().count()
    
    # Flag listings with 3 or more distinct reporters
    if report_count >= 3:
        # Add a visual flag in the admin (we'll add a field to the Listing model)
        listing.has_multiple_reports = True
        listing.save(update_fields=['has_multiple_reports'])
        
        # Could also auto-hide listings with too many reports
        # if report_count >= 5:
        #     listing.approved = False
        #     listing.rejection_reason = "Auto-hidden due to multiple reports"
        #     listing.save(update_fields=['approved', 'rejection_reason'])

@login_required
def toggle_favorite(request, pk):
    """Add or remove a listing from the user's favorites"""
    listing = get_object_or_404(Listing, pk=pk)
    user = request.user
    
    # Check if the listing is already in favorites
    favorite, created = Favorite.objects.get_or_create(user=user, listing=listing)
    
    if not created:
        # It was already favorited, so remove it
        favorite.delete()
        is_favorited = False
    else:
        # It's a new favorite
        is_favorited = True
    
    # If the request is AJAX, return JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'is_favorited': is_favorited,
            'count': listing.favorited_by.count()
        })
    
    # Otherwise redirect back to the referring page or listing detail
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('listing_detail', pk=pk)

@login_required
def favorites_list(request):
    """View for displaying a user's favorite listings"""
    favorites = Favorite.objects.filter(user=request.user).order_by('-date_added')
    ad_spaces = AdSpace.objects.filter(is_active=True)
    
    return render(request, 'listings/favorites.html', {
        'favorites': favorites,
        'ad_spaces': ad_spaces
    })