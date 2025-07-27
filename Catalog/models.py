from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ['name']

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    show_on_landing_page = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Sub Category"
        verbose_name_plural = "Sub Categories"
        ordering = ['category__name', 'name']
        unique_together = ['name', 'category']

    def __str__(self):
        return f"{self.category.name} - {self.name}"


class Article(models.Model):
    name = models.CharField(max_length=200)
    picture = models.ImageField(upload_to='articles/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles')
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles')
    tags = models.ManyToManyField(Tag, blank=True, related_name='articles')
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    number_of_sales_all_time = models.PositiveIntegerField(default=0)
    number_of_sales_this_month = models.PositiveIntegerField(default=0)
    colors_available = models.JSONField(default=list, blank=True)
    show_on_landing_page = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def total_revenue(self):
        """Calculate total revenue from all-time sales"""
        return self.price * self.number_of_sales_all_time


class Order(models.Model):
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='orders')
    number = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    size = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.pk} - {self.article.name}"

    @property
    def total_amount(self):
        """Calculate total order amount"""
        return self.article.price * self.number