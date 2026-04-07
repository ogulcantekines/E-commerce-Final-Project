from .models import Order

def cart_count(request):
    count = 0
    if request.user.is_authenticated:
        # Giriş yapmış kullanıcı için DB'den adetleri topla
        order = Order.objects.filter(user=request.user, is_completed=False).first()
        if order:
            # Tüm OrderItem'ların quantity alanlarını topluyoruz
            count = sum(item.quantity for item in order.items.all())
    else:
        # Misafir kullanıcı için session'a bak
        cart = request.session.get('cart', {})
        count = sum(cart.values())
        
    return {'cart_total_quantity': count}