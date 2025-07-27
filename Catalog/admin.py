from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Tag, Category, SubCategory, Article, Order


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'article_count']
    search_fields = ['name']
    ordering = ['name']
    
    def article_count(self, obj):
        count = obj.article_set.count()
        if count > 0:
            url = reverse('admin:catalog_article_changelist') + f'?tags__id__exact={obj.id}'
            return format_html('<a href="{}">{} articles</a>', url, count)
        return '0 articles'
    article_count.short_description = 'Articles Using This Tag'


class SubCategoryInline(admin.TabularInline):
    model = SubCategory
    extra = 1
    fields = ['name']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'subcategory_count']
    search_fields = ['name']
    ordering = ['name']
    inlines = [SubCategoryInline]
    
    def subcategory_count(self, obj):
        return obj.subcategories.count()
    subcategory_count.short_description = 'Subcategories'


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    list_filter = ['category']
    search_fields = ['name', 'category__name']
    ordering = ['category__name', 'name']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'sales_all_time', 'sales_this_month', 'colors_preview', 'tags_display']
    list_filter = ['tags', 'price']
    search_fields = ['name']
    filter_horizontal = ['tags']
    ordering = ['-number_of_sales_all_time']
    readonly_fields = ['number_of_sales_all_time', 'number_of_sales_this_month']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'price', 'tags')
        }),
        ('Inventory & Colors', {
            'fields': ('colors_available',),
            'description': 'Enter colors as a JSON list, e.g., ["Red", "Blue", "Green"]'
        }),
        ('Sales Statistics', {
            'fields': ('number_of_sales_all_time', 'number_of_sales_this_month'),
            'classes': ('collapse',)
        }),
    )
    
    def sales_all_time(self, obj):
        if obj.number_of_sales_all_time > 0:
            url = reverse('admin:catalog_order_changelist') + f'?article__id__exact={obj.id}'
            return format_html('<a href="{}">{}</a>', url, obj.number_of_sales_all_time)
        return '0'
    sales_all_time.short_description = 'Total Sales'
    
    def sales_this_month(self, obj):
        if obj.number_of_sales_this_month > 0:
            url = reverse('admin:catalog_order_changelist') + f'?article__id__exact={obj.id}'
            return format_html('<a href="{}">{}</a>', url, obj.number_of_sales_this_month)
        return '0'
    sales_this_month.short_description = 'Monthly Sales'
    
    def colors_preview(self, obj):
        if obj.colors_available:
            colors = obj.colors_available[:3]  # Show first 3 colors
            color_badges = []
            for color in colors:
                color_badges.append(f'<span style="background-color: {color.lower()}; color: white; padding: 2px 6px; border-radius: 3px; margin-right: 3px; font-size: 11px;">{color}</span>')
            
            result = ''.join(color_badges)
            if len(obj.colors_available) > 3:
                result += f'<span style="color: #666;">+{len(obj.colors_available) - 3} more</span>'
            return mark_safe(result)
        return 'No colors'
    colors_preview.short_description = 'Available Colors'
    
    def tags_display(self, obj):
        tags = obj.tags.all()[:3]  # Show first 3 tags
        if tags:
            tag_list = ', '.join([tag.name for tag in tags])
            if obj.tags.count() > 3:
                tag_list += f' (+{obj.tags.count() - 3} more)'
            return tag_list
        return 'No tags'
    tags_display.short_description = 'Tags'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer_name', 'article_link', 'quantity', 'size', 'color', 'total_amount', 'created_at']
    list_filter = ['created_at', 'article', 'size', 'color']
    search_fields = ['customer_name', 'customer_email', 'customer_phone', 'article__name']
    readonly_fields = ['created_at', 'order_summary']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Order Details', {
            'fields': ('article', 'number', 'size', 'color')
        }),
        ('Order Summary', {
            'fields': ('order_summary', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def order_number(self, obj):
        return f"#{obj.pk}"
    order_number.short_description = 'Order #'
    
    def article_link(self, obj):
        url = reverse('admin:catalog_article_change', args=[obj.article.pk])
        return format_html('<a href="{}">{}</a>', url, obj.article.name)
    article_link.short_description = 'Article'
    
    def quantity(self, obj):
        return obj.number
    quantity.short_description = 'Qty'
    
    def total_amount(self, obj):
        total = obj.article.price * obj.number
        return f"${total:.2f}"
    total_amount.short_description = 'Total'
    
    def order_summary(self, obj):
        total = obj.article.price * obj.number
        summary = f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0;">
            <h4 style="margin-top: 0;">Order Summary</h4>
            <p><strong>Customer:</strong> {obj.customer_name}</p>
            <p><strong>Email:</strong> {obj.customer_email}</p>
            <p><strong>Phone:</strong> {obj.customer_phone}</p>
            <p><strong>Article:</strong> {obj.article.name}</p>
            <p><strong>Price per item:</strong> ${obj.article.price}</p>
            <p><strong>Quantity:</strong> {obj.number}</p>
            <p><strong>Size:</strong> {obj.size}</p>
            <p><strong>Color:</strong> {obj.color}</p>
            <hr style="margin: 10px 0;">
            <p><strong>Total Amount:</strong> ${total:.2f}</p>
            <p><strong>Order Date:</strong> {obj.created_at.strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        """
        return mark_safe(summary)
    order_summary.short_description = 'Order Summary'


# Admin site customization
admin.site.site_header = 'Trycco Administration'
admin.site.site_title = 'Trycco Admin'
admin.site.index_title = 'Welcome to Trycco Administration'