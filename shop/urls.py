from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
   
    
    path('cart/', views.cart, name='cart'),
    path('add-to-cart/<slug:slug>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/<slug:slug>/', views.update_cart, name='update_cart'),
    path('remove-from-cart/<slug:slug>/', views.remove_from_cart, name='remove_from_cart'),

    path('checkout/', views.checkout, name='checkout'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),

    path('custom-cake/', views.custom_cake, name='custom_cake'),

    path('offers/', views.offers, name='offers'),
    path('gift-boxes/', views.gift_boxes, name='gift_boxes'),
    path('recipe/', views.recipe, name='recipe'),
    path('location/', views.location, name='location'),
    path('contact/', views.contact, name='contact'),
   
]

