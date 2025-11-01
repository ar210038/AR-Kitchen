from django.contrib import admin
from .models import Category, Flavor, Product, Order, Review, FAQ , Feedback
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
    
    # shop/admin.py
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'phone', 'total', 'delivery_method', 'payment_method', 'created', 'paid']
    list_filter = ['delivery_method', 'payment_method', 'created']
    readonly_fields = ['created']

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