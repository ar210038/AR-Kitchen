from django.db import models
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
     
    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:category_detail', args=[self.slug])


class Flavor(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    flavors = models.ManyToManyField(Flavor, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    featured = models.BooleanField(default=False)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    weight = models.CharField(max_length=50, blank=True, help_text="e.g. 1lbs, 500g, 2lb")
    
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.slug])

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    DELIVERY_CHOICES = [
        ('pickup', 'Pickup from Outlet'),
        ('delivery', 'Home Delivery (+৳100)'),
    ]
    

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.TextField(blank=True)
    delivery_method = models.CharField(max_length=10, choices=DELIVERY_CHOICES)
    delivery_date = models.DateField(help_text="When do you want your cake?")
    note = models.TextField(blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    
    def clean(self):
        if self.delivery_date < timezone.now().date():
            raise ValidationError("Delivery date cannot be in the past.")

    
    
    def __str__(self):
        return f"Order {self.id} - {self.name}"

    def send_confirmation_email(self):
        subject = f"Order Confirmed - #{self.id}"
        message = f"""
        Thank you {self.name}!

        Your order has been received.
        Total: ৳{self.total}
        Delivery: {self.get_delivery_method_display()}
        Payment: {self.get_payment_method_display()}

        We'll contact you soon at {self.phone}.
        """
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.email])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


# shop/models.py
from django.contrib.auth.models import User

class CustomCakeRequest(models.Model):
    WEIGHT_CHOICES = [
        ('0.5 lbs', '0.5 lbs'),
        ('1 lbs', '1 lbs'),
        ('2 lbs', '2 lbs'),
        ('3 lbs', '3+ lbs'),
    ]

    FLAVOR_CHOICES = [
        ('chocolate', 'Chocolate'),
        ('vanilla', 'Vanilla'),
        ('red_velvet', 'Red Velvet'),
        ('strawberry', 'Strawberry'),
        ('custom', 'Custom'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='custom_requests')
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    flavor = models.CharField(max_length=100)
    weight = models.CharField(max_length=10, choices=WEIGHT_CHOICES)
    message = models.TextField()
    design_image = models.ImageField(upload_to='custom_designs/', blank=True, null=True)
    note = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    replied = models.BooleanField(default=False)
    delivery_date = models.DateField(help_text="When do you want your cake?") 
    def __str__(self):
        return f"Custom Cake - {self.name} ({self.weight})"


class Review(models.Model):
    image = models.ImageField(upload_to='reviews/', help_text="Customer review screenshot")
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):  # ← FIXED INDENTATION
        return f"Review {self.id}"
    
# shop/models.py
class FAQ(models.Model):
    question = models.TextField()
    answer = models.TextField(blank=True)
    asked_by = models.CharField(max_length=100, blank=True)
    asked_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(null=True, blank=True)
    is_answered = models.BooleanField(default=False)

    class Meta:
        ordering = ['-is_answered', '-answered_at', '-asked_at']

    def __str__(self):
        return self.question[:50]    
    
# shop/models.py
class Feedback(models.Model):
    RATING_CHOICES = [(i, f"{i} Star{'s' if i > 1 else ''}") for i in range(1, 6)]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    rating = models.IntegerField(choices=RATING_CHOICES)
    photo = models.ImageField(upload_to='feedback/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-is_approved', '-created_at']

    def __str__(self):
        return f"{self.name} - {self.rating} stars"    
    