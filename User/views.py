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
from django.db.models import Q
from django.conf import settings
from mailjet_rest import Client
import os

logger = logging.getLogger(__name__)

def send_order_notification_email(order):
    """
    Send email notification to admin when a new order is created
    """
    try:
        # Initialize Mailjet client
        mailjet = Client(
            auth=(settings.MAILJET_API_KEY, settings.MAILJET_SECRET_KEY),
            version='v3.1'
        )
        
        # Prepare email data
        data = {
            'Messages': [
                {
                    "From": {
                        "Email": settings.MAILJET_FROM_EMAIL,
                        "Name": settings.MAILJET_FROM_NAME
                    },
                    "To": [
                        {
                            "Email": settings.ADMIN_EMAIL,
                            "Name": "Admin"
                        }
                    ],
                    "Subject": f"New Order #{order.pk} - {order.article.name}",
                    "HTMLPart": f"""
                    <h2>New Order Received</h2>
                    <p><strong>Order ID:</strong> #{order.pk}</p>
                    <p><strong>Date:</strong> {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
                    
                    <h3>Customer Information</h3>
                    <p><strong>Name:</strong> {order.customer_name}</p>
                    <p><strong>Email:</strong> {order.customer_email}</p>
                    <p><strong>Phone:</strong> {order.customer_phone}</p>
                    
                    <h3>Product Information</h3>
                    <p><strong>Product:</strong> {order.article.name}</p>
                    <p><strong>Category:</strong> {order.article.category.name if order.article.category else 'N/A'}</p>
                    <p><strong>Quantity:</strong> {order.number}</p>
                    <p><strong>Size:</strong> {order.size}</p>
                    <p><strong>Color:</strong> {order.color}</p>
                    <p><strong>Unit Price:</strong> {order.article.price} DA</p>
                    <p><strong>Total Amount:</strong> {order.total_amount} DA</p>
                    
                    <p>Please contact the customer to confirm delivery details.</p>
                    """,
                    "TextPart": f"""
                    New Order Received
                    
                    Order ID: #{order.pk}
                    Date: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}
                    
                    Customer Information:
                    Name: {order.customer_name}
                    Email: {order.customer_email}
                    Phone: {order.customer_phone}
                    
                    Product Information:
                    Product: {order.article.name}
                    Category: {order.article.category.name if order.article.category else 'N/A'}
                    Quantity: {order.number}
                    Size: {order.size}
                    Color: {order.color}
                    Unit Price: {order.article.price} DA
                    Total Amount: {order.total_amount} DA
                    
                    Please contact the customer to confirm delivery details.
                    """
                }
            ]
        }
        
        # Send email
        result = mailjet.send.create(data=data)
        
        if result.status_code == 200:
            logger.info(f"Order notification email sent successfully for order {order.pk}")
            return True
        else:
            logger.error(f"Failed to send order notification email for order {order.pk}: {result.json()}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending order notification email for order {order.pk}: {str(e)}")
        return False

# Create your views here.
def landingPage(request):
    carousel_articles = Article.objects.filter(show_on_landing_page=True).order_by('-created_at')[:5]
    categories = Category.objects.filter(show_on_landing_page=True).order_by('-created_at')[:5]
    return render(request, 'index.html', {'carousel_articles': carousel_articles, 'categories': categories})

def products(request):
    per_page = 9
    page = request.GET.get('page', 1)
    search = request.GET.get('search', '')
    sort = request.GET.get('sort', 'name')
    
    # Base queryset
    products = Article.objects.prefetch_related('tags').all()
    
    # Apply search filter
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(tags__name__icontains=search) |
            Q(category__name__icontains=search) |
            Q(subcategory__name__icontains=search)
        ).distinct()
    
    # Apply sorting
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    else:  # default to name
        products = products.order_by('name')
    
    # Paginate
    paginator = Paginator(products, per_page)
    page_obj = paginator.get_page(page)
    
    # Get additional data
    categories = Category.objects.order_by('-created_at')
    subcategories = SubCategory.objects.order_by('-created_at')
    tags = Tag.objects.order_by('-created_at')
    
    context = {
        'products': page_obj,
        'categories': categories, 
        'subcategories': subcategories,
        'tags': tags,
        'current_search': search,
        'current_sort': sort,
        'total_products': paginator.count,
    }
    
    return render(request, 'product-list.html', context)

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
                
                # Send email notification to admin
                send_order_notification_email(order)
                
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