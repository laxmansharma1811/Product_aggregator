import json
import subprocess
import sys
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
import matplotlib
from .scraper.hukut import scrape_products
from .models import *
from django.db.models import Q
import matplotlib.pyplot as plt
import io
import base64
from django.views.generic import TemplateView
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import csv
from pathlib import Path
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import update_session_auth_hash
from django.views.decorators.http import require_http_methods
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .scraper.hukut import scrape_products
from .scraper.utils import DarazScraper
import base64
import io
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .models import Product
import numpy as np
from django.contrib.auth.views import PasswordResetView
from django.utils.decorators import method_decorator
from collections import Counter

# Create your views here.

def clean_price(price_str):
    return float(price_str.replace('Rs.', '').replace('₹', '').replace(',', '').strip())

@login_required(login_url='login')
def home(request):
    # Get query parameters
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', '')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    
    # Start with all products
    products = Product.objects.all()
    
    # Filter by search query
    if search_query:
        products = products.filter(
            Q(product_name__icontains=search_query) |
            Q(specifications__icontains=search_query)
        )
    
    # Filter by price range
    if price_min or price_max:
        filtered_products = []
        for product in products:
            try:
                price = clean_price(product.product_price)
                if price_min and price < float(price_min):
                    continue
                if price_max and price > float(price_max):
                    continue
                filtered_products.append(product)
            except ValueError:
                # Handle cases where price cannot be converted
                continue
        products = filtered_products
    
    # Sort products
    if sort_by == 'price_low':
        products = sorted(products, key=lambda x: clean_price(x.product_price))
    elif sort_by == 'price_high':
        products = sorted(products, key=lambda x: clean_price(x.product_price), reverse=True)
    elif sort_by == 'rating':
        products = sorted(products, key=lambda x: x.rating, reverse=True)
    
    paginator = Paginator(products, 12)  # Show 12 products per page
    page = request.GET.get('page')
    
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Context for the template
    context = {
        'page_obj': page_obj,
        'products': products,
        'search_query': search_query,
        'sort_by': sort_by,
        'price_min': price_min,
        'price_max': price_max
    }
    
    return render(request, 'dashboard/home.html', context)

def about_us(request):
    return render(request, 'about/about_us.html')

def how_it_works(request):
    return render(request, 'about/how_it_works.html')

def faqs(request):
    return render(request, 'about/faqs.html')



@login_required(login_url='login')
def select_product(request, product_id):
    selected_products = request.session.get('selected_products', [])
    
    if product_id not in selected_products:
        if len(selected_products) >= 3:  # Limit of 3 products
            messages.warning(request, "You can only compare up to 3 products at a time.")
            return redirect('home')
            
        selected_products.append(product_id)
        request.session['selected_products'] = selected_products
        
    if len(selected_products) >= 2:  # Redirect when 2 or more products selected
        return redirect('comparison')
    
    return redirect('home')



@login_required(login_url='login')
def comparison(request):
    selected_product_ids = request.session.get('selected_products', [])
    products = Product.objects.filter(id__in=selected_product_ids)
    
    price_differences = []
    for i in range(len(products)):
        for j in range(i + 1, len(products)):
            diff = abs(clean_price(products[i].product_price) - clean_price(products[j].product_price))
            price_differences.append({
                'products': f'{products[i].product_name} vs {products[j].product_name}',
                'difference': diff
            })

    if request.method == 'POST' and 'clear_comparison' in request.POST:
        request.session['selected_products'] = []
        messages.success(request, "Comparison cleared.")
        return redirect('home')
    
    if request.method == 'POST' and 'remove_product' in request.POST:
        product_id = int(request.POST.get('remove_product'))
        selected_products = request.session.get('selected_products', [])
        if product_id in selected_products:
            selected_products.remove(product_id)
            request.session['selected_products'] = selected_products
            messages.success(request, "Product removed from comparison.")
            if len(selected_products) < 2:
                return redirect('home')
            return redirect('comparison')
    
    context = {
        'products': products,
        'price_differences': price_differences,
    }
    
    return render(request, 'comparison/comparison.html', context)




@login_required(login_url='login')
def analysis(request):
    # Fetch selected product IDs from the session
    selected_product_ids = request.session.get('selected_products', [])
    products = Product.objects.filter(id__in=selected_product_ids)

    if not products:
        messages.error(request, "No products selected for analysis.")
        return redirect('home')

    # Calculate price and rating differences
    price_differences = []
    rating_differences = []
    for i in range(len(products)):
        for j in range(i + 1, len(products)):
            price_diff = abs(clean_price(products[i].product_price) - clean_price(products[j].product_price))
            rating_diff = abs(products[i].rating - products[j].rating)
            price_differences.append({'products': f"{products[i].product_name} vs {products[j].product_name}", 'difference': price_diff})
            rating_differences.append({'products': f"{products[i].product_name} vs {products[j].product_name}", 'difference': rating_diff})

     # Handle product name duplication issue
    first_names = [p.product_name.split()[0] for p in products]
    name_counts = Counter(first_names)
    unique_names = []
    name_tracker = {}

    for name in first_names:
        if name_counts[name] > 1:
            count = name_tracker.get(name, 0) + 1
            name_tracker[name] = count
            unique_names.append(f"{name} {count}")  # Append index to duplicates
        else:
            unique_names.append(name)

    product_names = unique_names  # Use the modified names
    product_prices = [clean_price(p.product_price) for p in products]

    plt.figure(figsize=(8, 6))
    plt.bar(product_names, product_prices, color='skyblue')
    plt.xlabel("Products")
    plt.ylabel("Price (Rs.)")
    plt.title("Product Price Comparison")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    price_chart_url = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()

    # Generate a rating comparison bar chart
    product_ratings = [p.rating for p in products]

    plt.figure(figsize=(8, 6))
    plt.bar(product_names, product_ratings, color='lightgreen')
    plt.xlabel("Products")
    plt.ylabel("Rating")
    plt.title("Product Rating Comparison")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    rating_chart_url = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()

    # Calculate additional statistics
    avg_price = sum(product_prices) / len(product_prices) if product_prices else 0
    avg_rating = sum(product_ratings) / len(product_ratings) if product_ratings else 0
    max_price = max(product_prices, default=0)
    min_price = min(product_prices, default=0)
    max_rating = max(product_ratings, default=0)
    min_rating = min(product_ratings, default=0)

    # Calculate correlation between price and rating
    correlation = (
        round(np.corrcoef(product_prices, product_ratings)[0, 1], 2) 
        if len(products) > 1 else 0
    )

    # Find best value for money
    price_rating_ratios = [
        {'product': p.product_name, 'ratio': clean_price(p.product_price) / p.rating}
        for p in products if p.rating > 0
    ]
    best_value_product = min(price_rating_ratios, key=lambda x: x['ratio'], default=None)

    context = {
        'products': products,
        'price_differences': price_differences,
        'rating_differences': rating_differences,
        'price_chart_url': f"data:image/png;base64,{price_chart_url}",
        'rating_chart_url': f"data:image/png;base64,{rating_chart_url}",
        'avg_price': avg_price,
        'avg_rating': avg_rating,
        'max_price': max_price,
        'min_price': min_price,
        'max_rating': max_rating,
        'min_rating': min_rating,
        'correlation': correlation,
        'best_value_product': best_value_product,
        'product_prices': product_prices,  
        'product_ratings': product_ratings
    }

    return render(request, 'comparison/analysis.html', context)





@method_decorator(login_required(login_url='login'), name='dispatch')
class ProductSearchView(TemplateView):
    template_name = 'live/search.html'

    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        if query and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Scrape products
            scraper = DarazScraper()
            products = scraper.search_products(query, limit=5)

            # Save each product to the database
            for product in products:
                ScrapedProduct.objects.get_or_create(
                    product_link=product['product_link'],
                    defaults={
                        'image_url': product['image_url'],
                        'product_name': product['product_name'],
                        'product_price': product['product_price'],
                        'rating': product.get('rating'),
                        'number_of_ratings': product.get('number_of_ratings'),
                        'specifications': product.get('specifications'),
                    }
                )
            return JsonResponse({'products': products})

        return render(request, self.template_name)
    

@login_required(login_url='login')
def search_products(request):
    if request.method == "POST":
        query = request.POST.get('query')
        results = scrape_products(query)
        return JsonResponse({'products': results})
    return render(request, "live/hukut_live.html")



@login_required(login_url='login')
@csrf_exempt
def save_hukut_to_csv(request):
    if request.method == 'POST':
        try:
            product_data = json.loads(request.body)
            csv_path = 'product_aggregator/data/scraped_products.csv'
            
            # Ensure the directory exists
            Path(csv_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(csv_path, mode='a', newline='', encoding='utf-8') as file:
                fieldnames = ['Product Link', 'Image URL', 'Product Name', 'Product Price', 
                              'Rating', 'Number of Reviews', 'Specifications']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                
                # Create CSV row with default values for missing keys
                csv_row = {
                    'Product Link': product_data.get('product_link', ''),
                    'Image URL': product_data.get('image_url', ''),
                    'Product Name': product_data.get('product_name', ''),
                    'Product Price': product_data.get('product_price', ''),
                    'Rating': float(product_data.get('rating', 0)),  # Default to 0 if missing
                    'Number of Reviews': product_data.get('number_of_reviews', ''),  # Use correct key
                    'Specifications': product_data.get('specifications', '')
                }
                writer.writerow(csv_row)

            # Optionally run a management command
            subprocess.run([sys.executable, 'manage.py', 'load_default_csv'], check=True)

            return JsonResponse({'status': 'success', 'message': 'Hukut product saved to CSV and data loaded into database'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)




@login_required(login_url='login')    
@csrf_exempt
def save_to_csv(request):
    if request.method == 'POST':
        try:
            product_data = json.loads(request.body)
            csv_path = 'product_aggregator/data/scraped_products.csv'
            
            Path(csv_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(csv_path, mode='a', newline='', encoding='utf-8') as file:
                fieldnames = ['Product Link', 'Image URL', 'Product Name', 'Product Price', 
                            'Rating', 'Number of Ratings', 'Specifications']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                
                csv_row = {
                    'Product Link': product_data['product_link'],
                    'Image URL': product_data['image_url'],
                    'Product Name': product_data['product_name'],
                    'Product Price': product_data['product_price'],
                    'Rating': float(product_data['rating']),
                    'Number of Ratings': product_data['number_of_ratings'],
                    'Specifications': product_data['specifications']
                }
                writer.writerow(csv_row)

            # Run the management command to load the CSV data
            subprocess.run([sys.executable, 'manage.py', 'load_default_csv'], check=True)

            return JsonResponse({'status': 'success', 'message': 'Product saved to CSV and data loaded into database'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)




def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        first_name = request.POST.get('first_name')  
        last_name = request.POST.get('last_name')  

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = first_name  
        user.last_name = last_name    
        user.save()

         # Create user profile
        user_profile = UserProfile.objects.create(user=user, first_name=first_name, last_name=last_name)
        login(request, user)
        return redirect('login')

    return render(request, 'authentication/register.html')



def login_view(request):
    if request.method == "POST":
        identifier = request.POST.get('username')  # Can be either username or email
        password = request.POST.get('password')

        # Check if identifier is an email
        if User.objects.filter(email=identifier).exists():
            username = User.objects.get(email=identifier).username
        else:
            username = identifier

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username/email or password!")
            return redirect('login')

    return render(request, 'authentication/login.html')



@login_required(login_url='login')
def logout_view(request):
    logout(request)
    messages.success(request, "You have successfully logged out!")
    return redirect('login')





@login_required
def profile_view(request):
    # Get the user's profile, or create it if it doesn't exist
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Manually handle the form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        profile_picture = request.FILES.get('profile_picture')

        # Update the user profile with the new data
        if first_name:
            user_profile.first_name = first_name
        if last_name:
            user_profile.last_name = last_name
        if phone_number:
            user_profile.phone_number = phone_number
        if profile_picture:
            user_profile.profile_picture = profile_picture

        # Save the profile
        user_profile.save()

        return redirect('profile-view')  # Redirect to the profile page after saving

    return render(request, 'profile/profile.html', {'user_profile': user_profile})



@login_required(login_url='login')
def product_historical_data(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Fetch historical data
    historical_records = HistoricalData.objects.filter(product=product).order_by('date')

    historical_data = [
        {
            "date": record.date.strftime("%Y-%m-%d"),
            "price": record.price,
            "rating": record.rating,
        }
        for record in historical_records
    ]

    # Append current data
    current_data = {
        "date": "Current",  # Label as "Current"
        "price": float(product.product_price.replace(",", "").replace("Rs. ", "")),
        "rating": product.rating,
    }
    historical_data.append(current_data)

    context = {
        "product": product,
        "historical_records": list(historical_records) + [current_data],  # For the table
        "historical_data_json": json.dumps(historical_data),  # Pass JSON to the template
    }
    return render(request, "historical/product_detail.html", context)






class CustomPasswordResetView(PasswordResetView):
    email_template_name = 'registration/password_reset_email.html'

    def get_context_data(self, kwargs):
        context = super().get_context_data(kwargs)
        context['protocol'] = self.request.scheme  # 'http' or 'https'
        context['domain'] = self.request.get_host()  # Domain name (e.g., example.com)
        # Ensure uidb64 and token are passed to the context
        context['uidb64'] = kwargs.get('uidb64', '')
        context['token'] = kwargs.get('token', '')
        return context






@login_required
@require_http_methods(["GET", "POST"])
def change_password(request):
    if request.method == 'GET':
        return render(request, 'settings/change_password.html')
    
    old_password = request.POST.get('old_password')
    new_password = request.POST.get('new_password')
    
    if not request.user.check_password(old_password):
        return JsonResponse({'success': False, 'message': 'Old password is incorrect.'}, status=400)
    
    try:
        validate_password(new_password, request.user)
    except ValidationError as e:
        return JsonResponse({'success': False, 'message': ' '.join(e.messages)}, status=400)
    
    request.user.set_password(new_password)
    request.user.save()
    update_session_auth_hash(request, request.user)
    
    return JsonResponse({'success': True, 'message': 'Password changed successfully.'})

