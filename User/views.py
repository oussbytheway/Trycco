from django.shortcuts import render
from Catalog.models import *

# Create your views here.
def landingPage(request):
    carousel_articles = Article.objects.filter(show_on_landing_page=True).order_by('-created_at')[:5]
    categories = Category.objects.filter(show_on_landing_page=True).order_by('-created_at')[:5]
    return render(request, 'index.html', {'carousel_articles': carousel_articles, 'categories': categories})

def products(request):
    products = Article.objects.prefetch_related('tags').order_by('-created_at')
    categories = Category.objects.order_by('-created_at')
    subcategories = SubCategory.objects.order_by('-created_at')
    tags = Tag.objects.order_by('-created_at')
    
    return render(request, 'product-list.html', {
        'products': products, 
        'categories': categories, 
        'subcategories': subcategories,
        'tags': tags
    })