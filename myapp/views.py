from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.forms import PasswordChangeForm
from decimal import Decimal
from .models import Category, Product, Slider, Order, OrderItem, UserProfile, Review

# --- ANA SAYFA ---
def index(request):
    categories = Category.objects.all() 
    sliders = Slider.objects.filter(is_active=True)
    products = Product.objects.all().order_by('-id')[:4]
    return render(request, 'index.html', {'categories': categories, 'sliders': sliders, 'products': products})

# --- KATEGORİ VE ÜRÜN LİSTELEME ---
def category_list(request, category_slug):
    categories = Category.objects.all()
    category = get_object_or_404(Category, slug=category_slug)
    all_products = Product.objects.filter(category=category)
    available_brands = all_products.values_list('brand', flat=True).distinct()
    
    products = all_products
    secilen_markalar = request.GET.getlist('marka')
    if secilen_markalar:
        products = products.filter(brand__in=secilen_markalar)

    min_fiyat = request.GET.get('min_fiyat')
    max_fiyat = request.GET.get('max_fiyat')
    if min_fiyat: products = products.filter(price__gte=min_fiyat)
    if max_fiyat: products = products.filter(price__lte=max_fiyat)

    return render(request, "list.html", {'categories': categories, 'products': products, 'category': category, 'available_brands': available_brands})

def product_detail(request, product_slug):
    categories = Category.objects.all()
    product = get_object_or_404(Product, slug=product_slug)
    reviews = product.reviews.select_related('user').order_by('-created_at')
    user_review = reviews.filter(user=request.user).first() if request.user.is_authenticated else None
    avg_rating = round(sum(r.rating for r in reviews) / reviews.count(), 1) if reviews.count() > 0 else None
    return render(request, "details.html", {
        'categories': categories,
        'product': product,
        'reviews': reviews,
        'user_review': user_review,
        'avg_rating': avg_rating,
    })

# --- KULLANICI HESABI VE GİRİŞ/ÇIKIŞ ---
def user_account(request):
    categories = Category.objects.all()
    if request.method == "POST":
        if 'register_submit' in request.POST:
            ad_soyad, email, sifre, sifre_dogrula = request.POST.get('ad_soyad'), request.POST.get('email'), request.POST.get('sifre'), request.POST.get('sifre_dogrula')
            if sifre != sifre_dogrula:
                messages.error(request, "Şifreler eşleşmiyor!")
                return redirect('user_account')
            if User.objects.filter(username=email).exists():
                messages.error(request, "Bu email zaten kayıtlı!")
                return redirect('user_account')
            
            temp_cart = request.session.get('cart', {})
            user = User.objects.create_user(username=email, email=email, password=sifre)
            user.first_name = ad_soyad
            user.save()
            login(request, user)
            if temp_cart: request.session['cart'] = temp_cart
            return redirect('index')

        elif 'login_submit' in request.POST:
            email, sifre = request.POST.get('email'), request.POST.get('sifre')
            temp_cart = request.session.get('cart', {})
            user = authenticate(request, username=email, password=sifre)
            if user:
                login(request, user)
                if temp_cart: request.session['cart'] = temp_cart
                return redirect('index')
            messages.error(request, "Hatalı email veya şifre!")
    return render(request, "login.html", {'categories': categories})

def user_logout(request):
    logout(request)
    return redirect('index')

# --- SEPET İŞLEMLERİ ---
def cart(request):
    categories = Category.objects.all()
    cart_items, total_price = [], 0
    cart_session = request.session.get('cart', {})
    for p_id, qty in cart_session.items():
        try:
            product = Product.objects.get(id=int(p_id))
            item_total = product.price * qty
            total_price += item_total
            cart_items.append({'product': product, 'quantity': qty, 'item_total': item_total})
        except Product.DoesNotExist: continue
    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price, 'categories': categories})

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    p_id = str(product.id)
    cart_session = request.session.get('cart', {})
    cart_session[p_id] = cart_session.get(p_id, 0) + 1
    request.session['cart'] = cart_session
    request.session.modified = True
    messages.success(request, f"{product.name} sepete eklendi!")
    return redirect('cart')

def remove_from_cart(request, product_id):
    p_id = str(product_id)
    cart_session = request.session.get('cart', {})
    if p_id in cart_session:
        if cart_session[p_id] > 1: cart_session[p_id] -= 1
        else: del cart_session[p_id]
    request.session['cart'] = cart_session
    request.session.modified = True
    return redirect('cart')

def delete_cart_item(request, product_id):
    p_id = str(product_id)
    cart_session = request.session.get('cart', {})
    if p_id in cart_session: del cart_session[p_id]
    request.session['cart'] = cart_session
    request.session.modified = True
    return redirect('cart')

# --- ARAMA ---
def search(request):
    query = request.GET.get('q', '').strip()
    categories = Category.objects.all()
    products = Product.objects.filter(Q(name__icontains=query) | Q(brand__icontains=query)) if query else Product.objects.none()
    available_brands = products.values_list('brand', flat=True).distinct() if query else []
    return render(request, 'list.html', {'products': products, 'query': query, 'categories': categories, 'available_brands': available_brands})

# --- ÖDEME VE PROFİL ---
@login_required
def checkout_view(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    cart = request.session.get('cart', {})
    if not cart: return redirect('index')
    
    # Toplam fiyatı hesapla (session'da {product_id: quantity} formatında)
    cart_items = []
    total_price = Decimal('0.00')
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=int(product_id))
            item_total = product.price * quantity
            total_price += item_total
            cart_items.append({'product': product, 'quantity': quantity, 'item_total': item_total})
        except Product.DoesNotExist:
            continue

    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user,
            phone=request.POST.get('phone'),
            city=request.POST.get('city'),
            address=request.POST.get('address'),
            total_price=total_price,
            is_completed=True
        )
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['product'].price
            )
        request.session['cart'] = {}
        request.session.modified = True
        messages.success(request, 'Siparişiniz başarıyla oluşturuldu!')
        return redirect('orders')
    return render(request, 'checkout.html', {'profile': user_profile, 'total_price': total_price, 'cart_items': cart_items})

@login_required
def profile_view(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        user_profile.phone, user_profile.city, user_profile.address = request.POST.get('phone'), request.POST.get('city'), request.POST.get('address')
        user_profile.save()
        return redirect('profile')
    return render(request, 'profile.html', {'profile': user_profile})

@login_required
def orders(request):
    categories = Category.objects.all()
    user_orders = Order.objects.filter(user=request.user, is_completed=True).order_by('-created_at')
    return render(request, 'orders.html', {'categories': categories, 'orders': user_orders})

@login_required
def add_review(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '').strip()
        if comment and 1 <= rating <= 5:
            Review.objects.update_or_create(
                product=product,
                user=request.user,
                defaults={'rating': rating, 'comment': comment}
            )
            messages.success(request, 'Yorumunuz kaydedildi!')
        else:
            messages.error(request, 'Lütfen yorum ve puan giriniz.')
    return redirect('product_detail', product_slug=product_slug)

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_detail.html', {'order': order})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Oturum açık kalsın
            messages.success(request, 'Şifreniz başarıyla değiştirildi!')
            return redirect('profile')
        else:
            messages.error(request, 'Lütfen hataları düzeltin.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})