from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from Catalog.models import *
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
import logging
from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.db import transaction

logger = logging.getLogger(__name__)

# Create your views here.
def landingPage(request):
    carousel_articles = Article.objects.filter(show_on_landing_page=True).order_by('-created_at')[:5]
    categories = Category.objects.filter(show_on_landing_page=True).order_by('-created_at')[:5]
    return render(request, 'index.html', {'carousel_articles': carousel_articles, 'categories': categories})

@require_http_methods(["GET"])
def load_more_products(request):
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 9))
    
    # Calculate offset for better performance
    offset = (page - 1) * per_page
    
    # Only fetch the products we need
    products = Article.objects.prefetch_related('tags').order_by('-created_at')[offset:offset + per_page]
    
    # Get total count separately if needed
    total_count = Article.objects.count()
    has_more = offset + per_page < total_count
    
    products_data = []
    for product in products:
        product_data = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'picture': product.picture.url if product.picture else None,
            'colors_available': product.colors_available if hasattr(product, 'colors_available') else [],
            'sizes_available': product.sizes_available if hasattr(product, 'sizes_available') else [],
            'tags': [{'name': tag.name} for tag in product.tags.all()]
        }
        products_data.append(product_data)
    
    return JsonResponse({
        'products': products_data,
        'has_more': has_more,
        'current_page': page,
        'total_count': total_count
    })

def products(request):
    per_page = 9
    
    products = Article.objects.prefetch_related('tags').order_by('-created_at')
    categories = Category.objects.order_by('-created_at')
    subcategories = SubCategory.objects.order_by('-created_at')
    tags = Tag.objects.order_by('-created_at')
    
    # Paginate the initial products
    paginator = Paginator(products, per_page)
    page_obj = paginator.get_page(1)
    
    return render(request, 'product-list.html', {
        'products': page_obj,  # Use paginated products
        'categories': categories, 
        'subcategories': subcategories,
        'tags': tags,
        'has_more': page_obj.has_next()  # Pass info about more products
    })

def product_detail(request, id):
    """
    View to display detailed information about a specific product
    """
    try:
        # Get the product with related data to avoid additional queries
        product = Article.objects.select_related('category', 'subcategory').prefetch_related('tags').get(id=id)
    except Article.DoesNotExist:
        raise Http404("Product not found")
    
    # You might want to get related products for recommendations
    related_products = Article.objects.filter(
        category=product.category
    ).exclude(id=product.id)[:4]  # Get 4 related products
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    
    return render(request, 'product-detail.html', context)

def create_order(request, product_id):
    """
    View to handle order creation with message handling
    """
    if request.method == 'POST':
        try:
            # Get the product
            product = get_object_or_404(Article, id=product_id)
            
            # Validate form data
            customer_name = request.POST.get('customer_name', '').strip()
            customer_email = request.POST.get('customer_email', '').strip()
            customer_phone = request.POST.get('customer_phone', '').strip()
            size = request.POST.get('size', '').strip()
            color = request.POST.get('color', '').strip()
            
            try:
                number = int(request.POST.get('number', 1))
                if number <= 0:
                    raise ValueError("Quantity must be greater than 0")
            except (ValueError, TypeError):
                messages.error(
                    request, 
                    'Invalid quantity specified. Please enter a valid number.'
                )
                return redirect('product_detail', id=product_id)
            
            # Basic validation
            if not all([customer_name, customer_phone, size, color]):
                messages.error(
                    request, 
                    'Please fill in all required fields before placing your order.'
                )
                return redirect('product_detail', id=product_id)
            
            # Validate email format (basic check)
            if '@' not in customer_email or '.' not in customer_email.split('@')[-1]:
                messages.error(
                    request, 
                    'Please enter a valid email address.'
                )
                return redirect('product_detail', id=product_id)
            
            # Validate size and color are available for this product
            if size not in product.sizes_available:
                messages.error(
                    request, 
                    f'Size "{size}" is not available for this product.'
                )
                return redirect('product_detail', id=product_id)
            
            if color not in product.colors_available:
                messages.error(
                    request, 
                    f'Color "{color}" is not available for this product.'
                )
                return redirect('product_detail', id=product_id)
            
            # Use database transaction for data integrity
            with transaction.atomic():
                # Create the order
                order = Order.objects.create(
                    customer_name=customer_name,
                    customer_email=customer_email,
                    customer_phone=customer_phone,
                    article=product,
                    number=number,
                    size=size,
                    color=color
                )
                
                # Log successful order creation
                logger.info(f"Order {order.pk} created successfully for customer {customer_name}")
                
                # Add success message with order details
                messages.success(
                    request, 
                    f'🎉 Order #{order.pk} placed successfully! '
                    f'Total: {order.total_amount} DA. '
                    f'We will contact you at {customer_phone} to confirm delivery details.'
                )
                
                # Redirect back to product detail
                return redirect('product_detail', id=product_id)
        
        except Exception as e:
            # Log the error for debugging
            logger.error(f"Error creating order for product {product_id}: {str(e)}")
            
            # Add error message with contact information
            messages.error(
                request, 
                'We encountered an issue while processing your order. '
                'Please try again, or contact us directly to place your order manually.'
            )
            return redirect('product_detail', id=product_id)
    
    # If not POST, redirect to product detail
    return redirect('product_detail', id=product_id)