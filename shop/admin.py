from django.contrib import admin
from .models import Category, Flavor, Product, Order, Review, FAQ , Feedback, CustomCakeRequest
from django.utils.html import format_html
from django.utils import timezone


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'image_preview']  # Use preview
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['image_preview']  # Show in edit form

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height: 60px; width: auto; border-radius: 8px;">', obj.image.url)
        return "(No image)"
    image_preview.short_description = 'Image'

@admin.register(Flavor)
class FlavorAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'weight', 'featured', 'available']
    list_filter = ['category', 'featured', 'available']
    list_editable = ['price', 'featured', 'available']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['flavors']
    fields = ['name', 'slug', 'description', 'price', 'weight', 'image', 'category', 'flavors']
    
from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Order, OrderItem, Category
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ['product', 'quantity', 'price']
    readonly_fields = ['price']

    def has_add_permission(self, request, obj=None):
        return False 
    
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'phone', 'delivery_method', 'delivery_date', 'total', 'created']
    list_filter = ['delivery_method', 'delivery_date', 'created']
    search_fields = ['name', 'phone', 'id']
    readonly_fields = ['total', 'created']
    inlines = [OrderItemInline]
  

         
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_name_with_image', 'quantity', 'price']
    list_select_related = ['product', 'order']

    def product_name_with_image(self, obj):
        if obj.product.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" /> {}',
                obj.product.image.url, obj.product.name
            )
        return obj.product.name
    product_name_with_image.short_description = 'Cake'
    product_name_with_image.allow_tags = True

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ['product', 'quantity', 'price']
    readonly_fields = ['price']

    def has_add_permission(self, request, obj=None):
        return False
       
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'created']
    
@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'is_answered', 'asked_at', 'answered_at']
    list_filter = ['is_answered']
    search_fields = ['question', 'answer']
    readonly_fields = ['asked_by', 'asked_at']

    def save_model(self, request, obj, form, change):
        if obj.answer and not obj.is_answered:
            obj.is_answered = True
            obj.answered_at = timezone.now()
        super().save_model(request, obj, form, change)    
        
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'rating', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'rating']
    readonly_fields = ['name', 'email', 'message', 'rating', 'photo', 'created_at']
    actions = ['approve_feedback']

    def approve_feedback(self, request, queryset):
        queryset.update(is_approved=True)
    approve_feedback.short_description = "Approve selected feedback"        
    
# shop/admin.py
@admin.register(CustomCakeRequest)
class CustomCakeRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'phone', 'flavor', 'weight', 'delivery_date','created', 'replied']
    list_filter = ['weight', 'created', 'replied']
    search_fields = ['name', 'phone', 'email']
    readonly_fields = ['created']

    def mark_as_replied(self, request, queryset):
        queryset.update(replied=True)
    mark_as_replied.short_description = "Mark as replied"
    actions = [mark_as_replied]    