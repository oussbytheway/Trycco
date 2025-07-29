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
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="utf-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>New Order Notification</title>
                        <style>
                            body {{
                                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                                background-color: #1a1a1a;
                                color: #ffffff;
                                margin: 0;
                                padding: 20px;
                                line-height: 1.6;
                            }}
                            .container {{
                                max-width: 600px;
                                margin: 0 auto;
                                background-color: #2a2a2a;
                                border-radius: 10px;
                                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
                                overflow: hidden;
                            }}
                            .header {{
                                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                padding: 30px;
                                text-align: center;
                            }}
                            .header h1 {{
                                margin: 0;
                                color: white;
                                font-size: 28px;
                                font-weight: 600;
                            }}
                            .order-id {{
                                background-color: rgba(255, 255, 255, 0.2);
                                padding: 8px 16px;
                                border-radius: 20px;
                                display: inline-block;
                                margin-top: 10px;
                                font-weight: 500;
                            }}
                            .content {{
                                padding: 30px;
                            }}
                            .section {{
                                margin-bottom: 30px;
                                background-color: #333333;
                                border-radius: 8px;
                                padding: 20px;
                                border-left: 4px solid #667eea;
                            }}
                            .section h3 {{
                                margin-top: 0;
                                color: #667eea;
                                font-size: 18px;
                                font-weight: 600;
                                margin-bottom: 15px;
                                display: flex;
                                align-items: center;
                            }}
                            .section h3::before {{
                                content: '';
                                width: 8px;
                                height: 8px;
                                background-color: #667eea;
                                border-radius: 50%;
                                margin-right: 10px;
                            }}
                            .info-row {{
                                display: flex;
                                justify-content: space-between;
                                align-items: center;
                                padding: 8px 0;
                                border-bottom: 1px solid #404040;
                            }}
                            .info-row:last-child {{
                                border-bottom: none;
                            }}
                            .info-label {{
                                font-weight: 600;
                                color: #cccccc;
                                min-width: 120px;
                            }}
                            .info-value {{
                                color: #ffffff;
                                text-align: right;
                            }}
                            .phone-link {{
                                color: #667eea;
                                text-decoration: none;
                                font-weight: 500;
                                transition: color 0.3s ease;
                            }}
                            .phone-link:hover {{
                                color: #764ba2;
                                text-decoration: underline;
                            }}
                            .total-amount {{
                                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                color: white;
                                font-weight: bold;
                                font-size: 18px;
                                border-radius: 6px;
                                padding: 8px 12px;
                            }}
                            .footer {{
                                background-color: #333333;
                                padding: 20px;
                                text-align: center;
                                border-top: 1px solid #404040;
                            }}
                            .footer p {{
                                margin: 0;
                                color: #cccccc;
                                font-style: italic;
                            }}
                            .date {{
                                color: #999999;
                                font-size: 14px;
                                margin-top: 5px;
                            }}
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <div class="header">
                                <h1>🛍️ New Order Received</h1>
                                <div class="order-id">Order #{order.pk}</div>
                                <div class="date">{order.created_at.strftime('%B %d, %Y at %H:%M')}</div>
                            </div>
                            
                            <div class="content">
                                <div class="section">
                                    <h3>👤 Customer Information</h3>
                                    <div class="info-row">
                                        <span class="info-label">Name:</span>
                                        <span class="info-value">{order.customer_name}</span>
                                    </div>
                                    <div class="info-row">
                                        <span class="info-label">Email:</span>
                                        <span class="info-value">{order.customer_email}</span>
                                    </div>
                                    <div class="info-row">
                                        <span class="info-label">Phone:</span>
                                        <span class="info-value">
                                            <a href="tel:{order.customer_phone}" class="phone-link">
                                                📞 {order.customer_phone}
                                            </a>
                                        </span>
                                    </div>
                                </div>
                                
                                <div class="section">
                                    <h3>📦 Product Information</h3>
                                    <div class="info-row">
                                        <span class="info-label">Product:</span>
                                        <span class="info-value">{order.article.name}</span>
                                    </div>
                                    <div class="info-row">
                                        <span class="info-label">Category:</span>
                                        <span class="info-value">{order.article.category.name if order.article.category else 'N/A'}</span>
                                    </div>
                                    <div class="info-row">
                                        <span class="info-label">Quantity:</span>
                                        <span class="info-value">{order.number}</span>
                                    </div>
                                    <div class="info-row">
                                        <span class="info-label">Size:</span>
                                        <span class="info-value">{order.size}</span>
                                    </div>
                                    <div class="info-row">
                                        <span class="info-label">Color:</span>
                                        <span class="info-value">{order.color}</span>
                                    </div>
                                    <div class="info-row">
                                        <span class="info-label">Unit Price:</span>
                                        <span class="info-value">{order.article.price} DA</span>
                                    </div>
                                    <div class="info-row">
                                        <span class="info-label">Total Amount:</span>
                                        <span class="info-value total-amount">{order.total_amount} DA</span>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="footer">
                                <p>💬 Please contact the customer to confirm delivery details.</p>
                            </div>
                        </div>
                    </body>
                    </html>
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