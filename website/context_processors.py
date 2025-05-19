from .models import *

def cart_renderer(request):
    if not request.session.session_key:
        request.session.create()

    session_id = request.session.session_key

    try:
        cart = Cart.objects.get(session_id=session_id, completed=False)
    except Cart.DoesNotExist:
        cart = {"num_of_items": 0}

    return {"cart": cart}
