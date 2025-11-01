from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages  # ← ADD THIS
from .models import Product, Category, Review, FAQ , Feedback
from .forms import FAQForm
from .forms import FeedbackForm
from django.utils import timezone

def home(request):
    featured_products = Product.objects.filter(featured=True, available=True)[:6]
    categories = Category.objects.all()[:6]
    reviews = Review.objects.all().order_by('-created')
    slides = [reviews[i:i+4] for i in range(0, len(reviews), 4)]
    faqs = FAQ.objects.filter(is_answered=True)
    faq_form = FAQForm()
    if request.method == 'POST' and 'faq_submit' in request.POST:
        faq_form = FAQForm(request.POST)
        if faq_form.is_valid():
            faq_form.save()
            messages.success(request, "Question submitted! We'll answer soon.")
            return redirect('shop:home')
        
    feedbacks = Feedback.objects.filter(is_approved=True)[:6]  # Show 6 latest approved
    feedback_form = FeedbackForm()

    if request.method == 'POST' and 'feedback_submit' in request.POST:
        feedback_form = FeedbackForm(request.POST, request.FILES)
        if feedback_form.is_valid():
            feedback_form.save()
            messages.success(request, "Thank you! Your feedback is under review.")
            return redirect('shop:home')
    else:
        feedback_form = FeedbackForm()
            
    return render(request, 'shop/home.html', {
        'featured_products': featured_products,
        'categories': categories,
        'slides': slides,
        'faqs': faqs,
        'faq_form': faq_form,
        'feedbacks': feedbacks,
        'feedback_form': feedback_form,
    })
    

def shop(request):
    category_filter = request.GET.get('category')
    products = Product.objects.filter(available=True)
    if category_filter:
        products = products.filter(category__slug=category_filter)
    categories = Category.objects.all()
    return render(request, 'shop/shop.html', {
        'products': products,
        'categories': categories,
        'selected_category': category_filter
    })

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.filter(available=True)
    return render(request, 'shop/category.html', {
        'category': category,
        'products': products
    })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    return render(request, 'shop/product_detail.html', {'product': product})

# shop/views.py
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Product, Category, Flavor, Review

def shop(request):
    products = Product.objects.filter(available=True)
    categories = Category.objects.all()
    flavors = Flavor.objects.all()

    # FILTERS
    category_slug = request.GET.get('category')
    flavor_id = request.GET.get('flavor')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    if flavor_id:
        products = products.filter(flavors__id=flavor_id)

    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    context = {
        'products': products,
        'categories': categories,
        'flavors': flavors,
        'selected_category': category_slug,
        'selected_flavor': flavor_id,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'shop/shop.html', context)



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages


# ... your existing views ...

def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    cart = request.session.get('cart', {})
    
    # Add or increase quantity
    cart[slug] = cart.get(slug, 0) + 1
    request.session['cart'] = cart
    messages.success(request, f"{product.name} added to cart!")
    
    return redirect('shop:cart')

def cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    
    for slug, quantity in cart.items():
        product = get_object_or_404(Product, slug=slug)
        subtotal = product.price * quantity
        total += subtotal
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })
    
    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'total': total
    })

def update_cart(request, slug):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        quantity = int(request.POST.get('quantity', 0))
        
        if quantity > 0:
            cart[slug] = quantity
        else:
            cart.pop(slug, None)
        
        request.session['cart'] = cart
        messages.success(request, "Cart updated!")
    
    return redirect('shop:cart')

def remove_from_cart(request, slug):
    cart = request.session.get('cart', {})
    cart.pop(slug, None)
    request.session['cart'] = cart
    messages.success(request, "Item removed from cart.")
    return redirect('shop:cart')

# shop/views.py
from .forms import CheckoutForm, CustomCakeForm
from .models import Order, OrderItem

def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('shop:shop')

    # Calculate total
    total = 0
    cart_items = []
    for slug, qty in cart.items():
        product = get_object_or_404(Product, slug=slug)
        subtotal = product.price * qty
        total += subtotal
        cart_items.append({'product': product, 'quantity': qty, 'subtotal': subtotal})

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.total = total
            order.save()

            # Save items
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['product'].price,
                    quantity=item['quantity']
                )

            # Clear cart
            request.session['cart'] = {}
            messages.success(request, f"Order #{order.id} placed! We'll call you soon.")
            return redirect('shop:order_success', order_id=order.id)
    else:
        form = CheckoutForm()

    return render(request, 'shop/checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'total': total
    })

def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'shop/order_success.html', {'order': order})

from django.core.paginator import Paginator
from django.core.mail import send_mail

def shop(request):
    products = Product.objects.filter(available=True)
    categories = Category.objects.all()
    flavors = Flavor.objects.all()

    # SEARCH
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )

    # FILTERS (existing)
    category_slug = request.GET.get('category')
    flavor_id = request.GET.get('flavor')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if category_slug:
        products = products.filter(category__slug=category_slug)
    if flavor_id:
        products = products.filter(flavors__id=flavor_id)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # PAGINATION
    paginator = Paginator(products, 9)  # 6 per page
    page = request.GET.get('page')
    products = paginator.get_page(page)

    context = {
        'products': products,
        'categories': categories,
        'flavors': flavors,
        'query': query,
        'selected_category': category_slug,
        'selected_flavor': flavor_id,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'shop/shop.html', context)

def custom_cake(request):
    if request.method == 'POST':
        form = CustomCakeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Custom cake request sent! We'll call you.")
            return redirect('shop:shop')
    else:
        form = CustomCakeForm()
    return render(request, 'shop/custom_cake.html', {'form': form})


def offers(request):
    # Show featured/discount products
    products = Product.objects.filter(featured=True, available=True)
    return render(request, 'shop/offers.html', {'products': products})

def gift_boxes(request):
    return render(request, 'shop/gift_boxes.html')

def recipe(request):
    return render(request, 'shop/recipe.html')

def location(request):
    return render(request, 'shop/location.html')

def contact(request):
    if request.method == 'POST':
        # Simple contact form
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        send_mail(
            f"Contact Form: {name}",
            f"From: {email}\n\n{message}",
            email,
            ['contact@arkitchen.com'],
        )
        messages.success(request, "Message sent! We'll reply soon.")
        return redirect('shop:contact')
    return render(request, 'shop/contact.html')



