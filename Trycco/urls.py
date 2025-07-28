from django.contrib import admin
from django.urls import path
from User.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', landingPage, name='landing_page'),
    path('products/', products, name='products'),
    path('product/<int:id>/', product_detail, name='product_detail'),
    path('product/<int:product_id>/order/', create_order, name='create_order'),
    path('load-more-products/', load_more_products, name='load_more_products')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
