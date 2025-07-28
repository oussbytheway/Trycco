from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from Catalog.models import *
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
import logging
from django.shortcuts import render, get_object_or_404
from django.http import Http404

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
    View to handle order creation
    """
    if request.method == 'POST':
        try:
            # Get the product
            product = get_object_or_404(Article, id=product_id)
            
            # Create the order
            order = Order.objects.create(
                customer_name=request.POST.get('customer_name'),
                customer_email=request.POST.get('customer_email'),
                customer_phone=request.POST.get('customer_phone'),
                article=product,
                number=int(request.POST.get('number', 1)),
                size=request.POST.get('size'),
                color=request.POST.get('color')
            )
            
            # Add success message
            messages.success(
                request, 
                f'Order #{order.pk} placed successfully! Total: {order.total_amount} DA'
            )
            
            # Redirect back to product detail or to an order confirmation page
            return redirect('product_detail', id=product_id)
            
        except Exception as e:
            messages.error(request, 'There was an error placing your order. Please try again.')
            return redirect('product_detail', id=product_id)
    
    # If not POST, redirect to product detail
    return redirect('product_detail', id=product_id)