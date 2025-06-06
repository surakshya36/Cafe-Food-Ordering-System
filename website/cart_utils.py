# cart_utils.py

from .models import Cart

def get_or_create_cart(request, cart_type='normal'):
    if not request.session.session_key:
        request.session.create()

    session_id = request.session.session_key
    if cart_type == 'vip':
        session_id = f"vip_{session_id}"

    cart, _ = Cart.objects.get_or_create(
        session_id=session_id,
        completed=False,
        defaults={'cart_type': cart_type}
    )
    return cart

