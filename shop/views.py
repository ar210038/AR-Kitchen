from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages  # ← ADD THIS
from .models import Product, Category, Review, FAQ , Feedback
from .forms import FAQForm, FeedbackForm, CustomCakeForm
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

# shop/views.py
from django.http import JsonResponse

def add_to_cart(request, slug):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request'})

    product = get_object_or_404(Product, slug=slug, available=True)
    cart = request.session.get('cart', {})
    
    # Add or increase quantity
    qty = int(request.POST.get('quantity', 1))
    cart[slug] = cart.get(slug, 0) + qty
    request.session['cart'] = cart
    request.session.modified = True  # Important for session

    # Calculate total items
    total_items = sum(cart.values())

    return JsonResponse({
        'success': True,
        'message': f"{product.name} added to cart!",
        'cart_count': total_items
    })

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

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .forms import CheckoutForm
from .models import Order, OrderItem, Product
from django.contrib.auth import login
from django.contrib.auth.models import User



def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('shop:shop')

    # === CALCULATE CART ITEMS ===
    cart_items = []
    subtotal = 0
    for slug, qty in cart.items():
        product = get_object_or_404(Product, slug=slug)
        item_total = product.price * qty
        subtotal += item_total
        cart_items.append({
            'product': product,
            'quantity': qty,
            'subtotal': item_total
        })

    # === INITIAL FORM DATA (BEFORE POST) ===
    initial_data = {'delivery_date': timezone.now().date()}
    if request.user.is_authenticated:
        initial_data.update({
            'name': request.user.get_full_name() or request.user.username,
            'phone': getattr(request.user, 'phone', ''),
            'email': request.user.email or '',
        })

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        create_account = request.POST.get('create_account')

        if form.is_valid():
            order = form.save(commit=False)
            
            # === LINK TO LOGGED-IN USER ===
        if request.user.is_authenticated:
            order.user = request.user  # ← ADD THIS
            # Optional: override form data with user data
            if not order.phone:
                order.phone = request.user.phone
            if not order.name:
                order.name = request.user.get_full_name() or request.user.username
            
            # === DELIVERY FEE ===
            delivery_fee = 100 if order.delivery_method == 'delivery' else 0
            order.total = subtotal + delivery_fee
            order.save()

            # === CREATE ACCOUNT IF CHECKED ===
            if create_account and not request.user.is_authenticated:
                phone = form.cleaned_data['phone']
                password = User.objects.make_random_password()
                user = User.objects.create_user(username=phone, password=password)
                user.phone = phone
                user.email = form.cleaned_data.get('email', '')
                user.save()
                login(request, user)
                messages.info(request, f"Account created! Username: {phone}")

            # === SAVE ORDER ITEMS ===
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['product'].price,
                    quantity=item['quantity']
                )

            # === CLEAR CART ===
            request.session['cart'] = {}
            messages.success(request, f"Order #{order.id} placed!")
            return redirect('shop:order_success', order_id=order.id)
    else:
        form = CheckoutForm(initial=initial_data)

    # === TOTAL FOR DISPLAY (LIVE UPDATE VIA JS) ===
    delivery_method = request.POST.get('delivery_method') if request.method == 'POST' else 'pickup'
    total = subtotal + (100 if delivery_method == 'delivery' else 0)

    context = {
        'form': form,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total': total,
    }
    return render(request, 'shop/checkout.html', context)

# shop/views.py
from django.shortcuts import render, get_object_or_404
from .models import Order

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

# shop/views.py
from .forms import CustomCakeForm
from .models import CustomCakeRequest

def custom_cake(request):
    if request.method == 'POST':
        form = CustomCakeForm(request.POST, request.FILES)
        if form.is_valid():
            custom = form.save(commit=False)
            if request.user.is_authenticated:
                custom.user = request.user
                if not custom.phone:
                    custom.phone = request.user.phone
                if not custom.name:
                    custom.name = request.user.get_full_name() or request.user.username
                if not custom.email:
                    custom.email = request.user.email
            custom.save()
            messages.success(request, "Your custom cake request has been sent!")
            return redirect('shop:shop')
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {
                'name': request.user.get_full_name() or request.user.username,
                'phone': request.user.phone,
                'email': request.user.email,
            }
        form = CustomCakeForm(initial=initial)

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



