from .models import Order

def cart_count(request):
    """Sepetteki toplam ürün adedini döndürür (session-based)."""
    cart = request.session.get('cart', {})
    count = sum(cart.values())
    return {'cart_total_quantity': count}