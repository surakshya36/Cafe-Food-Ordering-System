from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import MenuItem, Cart,CartItem
from categories.models import Category
from django.urls import reverse
from django.http import Http404, JsonResponse
import json
import uuid
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from decimal import Decimal
from django.db import transaction
from .models import Cart
from orders.models import Order, OrderItem
from menuitems.models import MenuItem
from tables.models import Table
from tables.models import Room
from user_staff.models import Notification  
from .cart_utils import get_or_create_cart



def menu_for_customers(request):
    search_query = request.GET.get('search', '').strip()
    is_search = bool(search_query)

    # Base queryset
    menu_items = MenuItem.objects.filter(is_available=True)
    order = get_current_order(request)

    if is_search:
        # Enhanced search across multiple fields
        menu_items = menu_items.filter(
        Q(name__icontains=search_query) |
        Q(description__icontains=search_query) |
        Q(category__name__icontains=search_query),
        ~Q(vip_status='VIP_ONLY')  # Exclude VIP_ONLY from search
        ).select_related('category')

        special_items = None
    else:
        special_items = menu_items.filter(
            vip_status='TODAYS_SPECIAL'
        ).select_related('category')
        
        menu_items = menu_items.filter(
            vip_status__in=['REGULAR', 'TODAYS_SPECIAL']
        ).select_related('category')

    # Sorting and filtering
    categories = Category.objects.filter(is_active=True)
    sort_by = request.GET.get('sort', 'name')
    category_id = request.GET.get('category')

    if category_id:
        menu_items = menu_items.filter(category_id=category_id)

    if sort_by == 'price_asc':
        menu_items = menu_items.order_by('price')
    elif sort_by == 'price_desc':
        menu_items = menu_items.order_by('-price')
    elif sort_by == 'time':
        menu_items = menu_items.order_by('preparation_time')
    else:
        menu_items = menu_items.order_by('name')

    return render(request, 'website/menu_lists.html', {
        'menu_items': menu_items,
        'order': order,
        'special_items': special_items,
        'categories': categories,
        'current_sort': sort_by,
        'current_category': category_id,
        'search_term': search_query,
        'is_search': is_search,
        'page': 'Menu'
    })


def menu_for_vipcustomers(request):
    search_query = request.GET.get('search', '').strip()
    is_search = bool(search_query)

    # Base queryset
    menu_items = MenuItem.objects.filter(is_available=True)
    order = get_current_order(request)

    if is_search:
        # Enhanced search across multiple fields
        menu_items = menu_items.filter(
        Q(name__icontains=search_query) |
        Q(description__icontains=search_query) |
        Q(category__name__icontains=search_query)
    ).select_related('category')

        special_items = None
    else:
        special_items = menu_items.filter(
            vip_status='TODAYS_SPECIAL'
        ).select_related('category')
        
        menu_items = menu_items.filter(
            vip_status__in=['REGULAR', 'TODAYS_SPECIAL', 'VIP_ONLY']  # Explicitly add VIP_ONLY here
        ).select_related('category')

    # Sorting and filtering
    categories = Category.objects.filter(is_active=True)
    sort_by = request.GET.get('sort', 'name')
    category_id = request.GET.get('category')

    if category_id:
        menu_items = menu_items.filter(category_id=category_id)

    if sort_by == 'price_asc':
        menu_items = menu_items.order_by('price')
    elif sort_by == 'price_desc':
        menu_items = menu_items.order_by('-price')
    elif sort_by == 'time':
        menu_items = menu_items.order_by('preparation_time')
    else:
        menu_items = menu_items.order_by('name')

    return render(request, 'website/vip/menu_lists.html', {
        'menu_items': menu_items,
        'order': order,
        'special_items': special_items,
        'categories': categories,
        'current_sort': sort_by,
        'current_category': category_id,
        'search_term': search_query,
        'is_search': is_search,
        'page': 'Vip-Menu'
    })


def item_detail(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id, is_available=True)
    search_query = request.GET.get('search', '').strip()  # Get search query if exists
   
    # Recommended items with search preservation
    recommended_items = MenuItem.objects.filter(
        is_available=True,
        category=item.category,
        vip_status='REGULAR'  # Only regular items
    ).exclude(id=item.id)[:4]
    
    return render(request, 'website/menu_item_card.html', {
        'item': item,
        'recommended_items': recommended_items,
        'search_term': search_query,  # Pass to template
        'page': 'Item Detail',
    })

def vip_item_detail(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id, is_available=True)
    search_query = request.GET.get('search', '').strip()  # Get search query if exists
   
    # Recommended items with search preservation
    recommended_items = MenuItem.objects.filter(
        is_available=True,
        category=item.category,
        vip_status='REGULAR'  # Only regular items
    ).exclude(id=item.id)[:4]
    
    return render(request, 'website/vip/menu_item_card.html', {
        'item': item,
        'recommended_items': recommended_items,
        'search_term': search_query,  # Pass to template
        'page': 'Item Detail',
    })


def handle_search(request): 
    """Redirect to menu page with search query"""
    search_query = request.GET.get('search', '').strip()
    return redirect(f"{reverse('customer_menu')}?search={search_query}")


def vip_handle_search(request): 
    """Redirect to menu page with search query"""
    search_query = request.GET.get('search', '').strip()
    return redirect(f"{reverse('menu_for_vipcustomers')}?search={search_query}")

def get_cart_key(request):
    if request.session.get('is_vip'):
        return 'vip_cart'
    return 'normal_cart'


def cart(request):
    cart = get_or_create_cart(request, cart_type='normal')

    cart_items = cart.cartitems.select_related('item')
    subtotal = cart.total_price
    total_quantity = cart.num_of_items

    available_rooms = Room.objects.filter(is_active=True).order_by('room_type', 'name')
    initial_room = available_rooms.first()
    available_tables = Table.objects.filter(
        room=initial_room,
        status='AVAILABLE'
    ).order_by('table_number') if initial_room else []

    current_order = get_current_order(request)

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'available_rooms': available_rooms,
        'available_tables': available_tables,
        'total_quantity': total_quantity,
        'current_order': current_order,
        'page': 'Your Cart',
    }

    return render(request, 'website/cart.html', context)




def add_to_cart(request):
    # Load JSON data from request
    data = json.loads(request.body)
    item_id = data.get("id")
    
    try:
        item = MenuItem.objects.get(id=item_id)
        
        cart = get_or_create_cart(request, cart_type='normal')
        
        # Get or create cart item
        cartitem, created = CartItem.objects.get_or_create(cart=cart, item=item)
        cartitem.quantity += 1
        cartitem.save()
        
        # Prepare success response
        response_data = {
            'success': True,
            'message': f"{item.name} has been added to your cart successfully!",
            'cart_total': cart.num_of_items,
            'item_name': item.name,
            'new_quantity': cartitem.quantity
        }
        
        return JsonResponse(response_data)
        
    except MenuItem.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Item not found'
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
    
def vip_cart(request):
    cart = get_or_create_cart(request, cart_type='vip')

    cart_items = cart.cartitems.select_related('item')
    subtotal = cart.total_price
    total_quantity = cart.num_of_items

    available_rooms = Room.objects.filter(is_active=True).order_by('room_type', 'name')
    initial_room = available_rooms.first()
    available_tables = Table.objects.filter(
        room=initial_room,
        status='AVAILABLE'
    ).order_by('table_number') if initial_room else []

    current_order = vip_get_current_order(request)

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'available_rooms': available_rooms,
        'available_tables': available_tables,
        'total_quantity': total_quantity,
        'current_order': current_order,
        'page': 'Your Cart',
    }
    print("Current VIP Order:", current_order)
    return render(request, 'website/vip/cart.html', context)


    
def vip_add_to_cart(request):
    data = json.loads(request.body)
    item_id = data.get("id")

    try:
        item = MenuItem.objects.get(id=item_id)

        cart = get_or_create_cart(request, cart_type='vip')

        cartitem, created = CartItem.objects.get_or_create(cart=cart, item=item)
        cartitem.quantity += 1
        cartitem.save()

        response_data = {
            'success': True,
            'message': f"{item.name} has been added to your cart successfully!",
            'cart_total': cart.num_of_items,
            'item_name': item.name,
            'new_quantity': cartitem.quantity
        }

        return JsonResponse(response_data)

    except MenuItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Item not found'}, status=404)

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


    
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Cart, CartItem, MenuItem
from django.shortcuts import get_object_or_404


@require_POST
def vip_increase_quantity(request, item_id):
    try:
        cart = get_or_create_cart(request, cart_type='vip')
        cart_item = get_object_or_404(CartItem, cart=cart, item_id=item_id)

        cart_item.quantity += 1
        cart_item.save()

        return JsonResponse({
            'success': True,
            'message': f"{cart_item.item.name} quantity increased.",
            'new_quantity': cart_item.quantity,
            'subtotal': cart_item.price,
            'cart_total': cart.num_of_items,
            'total_price': cart.total_price
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@require_POST
def increase_quantity(request, item_id):
    try:
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, cart=cart, item_id=item_id)

        cart_item.quantity += 1
        cart_item.save()

        return JsonResponse({
            'success': True,
            'message': f"{cart_item.item.name} quantity increased.",
            'new_quantity': cart_item.quantity,
            'subtotal': cart_item.price,
            'cart_total': cart.num_of_items,
            'total_price': cart.total_price
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
@require_POST
def vip_decrease_quantity(request, item_id):
    try:
        cart = get_or_create_cart(request, cart_type='vip')
        cart_item = get_object_or_404(CartItem, cart=cart, item_id=item_id)

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            new_quantity = cart_item.quantity
            subtotal = cart_item.price
            removed = False
            message = f"{cart_item.item.name} quantity decreased."
        else:
            cart_item.delete()
            new_quantity = 0
            subtotal = 0
            removed = True
            message = f"{cart_item.item.name} removed from cart."

        return JsonResponse({
            'success': True,
            'message': message,
            'new_quantity': new_quantity,
            'subtotal': subtotal,
            'cart_total': cart.num_of_items,
            'total_price': cart.total_price,
            'removed': removed
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@require_POST
def decrease_quantity(request, item_id):
    try:
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, cart=cart, item_id=item_id)

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            new_quantity = cart_item.quantity
            subtotal = cart_item.price
            removed = False
            message = f"{cart_item.item.name} quantity decreased."
        else:
            cart_item.delete()
            new_quantity = 0
            subtotal = 0
            removed = True
            message = f"{cart_item.item.name} removed from cart."

        return JsonResponse({
            'success': True,
            'message': message,
            'new_quantity': new_quantity,
            'subtotal': subtotal,
            'cart_total': cart.num_of_items,
            'total_price': cart.total_price,
            'removed': removed
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@require_POST
def vip_remove_item(request, item_id):
    try:
        cart = get_or_create_cart(request, cart_type='vip')
        cart_item = get_object_or_404(CartItem, cart=cart, item_id=item_id)
        item_name = cart_item.item.name
        cart_item.delete()

        return JsonResponse({
            'success': True,
            'message': f"{item_name} removed from cart.",
            'cart_total': cart.num_of_items,
            'total_price': cart.total_price,
            'removed': True
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
@require_POST
def remove_item(request, item_id):
    try:
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, cart=cart, item_id=item_id)
        item_name = cart_item.item.name
        cart_item.delete()

        return JsonResponse({
            'success': True,
            'message': f"{item_name} removed from cart.",
            'cart_total': cart.num_of_items,
            'total_price': cart.total_price,
            'removed': True
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
@require_POST
def vip_empty_cart(request):
    try:
        cart = get_or_create_cart(request, cart_type='vip')
        cart.cartitems.all().delete()

        return JsonResponse({
            'success': True,
            'message': "Cart emptied successfully.",
            'cart_total': 0,
            'total_price': 0
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
@require_POST
def empty_cart(request):
    try:
        cart = get_or_create_cart(request)
        cart.cartitems.all().delete()

        return JsonResponse({
            'success': True,
            'message': "Cart emptied successfully.",
            'cart_total': 0,
            'total_price': 0
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from decimal import Decimal
from django.db import transaction
from .models import Cart
from tables.models import Table
from orders.models import Order, OrderItem
@require_POST
def show_confirm_order(request):
    if not request.session.session_key:
        request.session.create()

    try:
        cart = get_or_create_cart(request, cart_type='normal')
    except Cart.DoesNotExist:
        messages.error(request, "Your cart is empty")
        return redirect('cart')

    if not cart.cartitems.exists():
        messages.error(request, "Your cart is empty")
        return redirect('cart')

    customer_name = request.POST.get('customer_name', 'Guest')
    table_number = request.POST.get('table_number', '1')
    room_number = request.POST.get('room_number', '')
    special_requests = request.POST.get('special_requests', '')
    is_rush = request.POST.get('rush_order', 'false') == 'true'

    subtotal = cart.total_price
    service_charge_percent = Decimal('0.15') if is_rush else Decimal('0.10')

    # ✅ Discount Logic
    if subtotal < 500:
        discount_percent = Decimal('0.00')
    elif subtotal <= 1000:
        discount_percent = Decimal('0.02')
    elif subtotal <= 5000:
        discount_percent = Decimal('0.06')
    else:
        discount_percent = Decimal('0.10')

    discount_amount = subtotal * discount_percent
    subtotal_after_discount = subtotal - discount_amount

    # ✅ Recalculate taxes on discounted subtotal
    vat_amount = subtotal_after_discount * Decimal('0.13')
    service_tax = subtotal_after_discount * service_charge_percent

    total_with_tax = subtotal_after_discount + vat_amount + service_tax

    order_items = []
    for item in cart.cartitems.select_related('item').all():
        order_items.append({
            'name': item.item.name,
            'quantity': item.quantity,
            'price': item.item.price,
            'subtotal': item.item.price * item.quantity,
            'image': item.item.image.url if item.item.image else None
        })

    return render(request, 'website/confirm_order.html', {
        'cart': cart,
        'order_items': order_items,
        'customer_name': customer_name,
        'table_number': table_number,
        'room_number': room_number,
        'special_requests': special_requests,
        'is_rush': is_rush,
        'subtotal': subtotal,
        'discount_percent': int(discount_percent * 100),
        'discount_amount': discount_amount,
        'subtotal_after_discount': subtotal_after_discount,
        'vat_amount': vat_amount,
        'service_tax': service_tax,
        'total_with_tax': total_with_tax,
        'total_quantity': sum(item.quantity for item in cart.cartitems.all()),
        'service_charge_percent': int(service_charge_percent * 100)
    })

from decimal import Decimal
from django.db import transaction


@require_POST
def process_order(request):
    if not request.session.session_key:
        request.session.create()

    try:
        cart = get_or_create_cart(request, cart_type='normal')
    except Cart.DoesNotExist:
        messages.error(request, "Your cart is empty")
        return redirect('cart')

    if not cart.cartitems.exists():
        messages.error(request, "Your cart is empty")
        return redirect('cart')

    try:
        with transaction.atomic():
            customer_name = request.POST.get('customer_name')
            table_number = request.POST.get('table_number')
            room_number = request.POST.get('room_number', '')  # room name or number
            special_requests = request.POST.get('special_requests', '')
            is_rush = request.POST.get('is_rush', 'false') == 'true'
            session_key = request.session.session_key

            if not room_number:
                raise ValueError("Room number is required to select a table")

            table = Table.objects.get(table_number=table_number, room__name=room_number)

            # Check if table is AVAILABLE or not
            if table.status != 'AVAILABLE':
                # Check if existing active order belongs to the same session
                active_order_for_table = Order.objects.filter(
                    table=table,
                    status__in=['PENDING', 'CONFIRMED', 'PREPARING', 'READY', 'SERVED']
                ).first()

                if active_order_for_table:
                    if active_order_for_table.session_key != session_key:
                        # Active order belongs to different session - block
                        raise ValueError(f"Table {table_number} is currently occupied by another customer.")
                    # else: same session, allow new order

            # Calculate subtotal and discounts
            subtotal = cart.total_price

            if subtotal < 500:
                vip_discount_percent = Decimal('0.00')
            elif subtotal <= 1000:
                vip_discount_percent = Decimal('0.02')
            elif subtotal <= 5000:
                vip_discount_percent = Decimal('0.06')
            else:
                vip_discount_percent = Decimal('0.10')

            discount_amount = subtotal * vip_discount_percent
            subtotal_after_discount = subtotal - discount_amount

            vat = subtotal_after_discount * Decimal('0.13')
            service_charge_percent = Decimal('0.15') if is_rush else Decimal('0.10')
            service_charge = subtotal_after_discount * service_charge_percent

            total_amount = subtotal_after_discount + vat + service_charge

            # Create new order
            order = Order.objects.create(
                table=table,
                customer_name=customer_name,
                special_requests=special_requests,
                total_amount=total_amount,
                vip_discount=discount_amount,
                is_rush=is_rush,
                order_type='normal',
                status='PENDING',
                session_key=session_key
            )

            # Create order items and decrease stock quantity
            for cart_item in cart.cartitems.select_related('item').all():
                if not cart_item.item.decrease_quantity(cart_item.quantity):
                    raise ValueError(f"Insufficient quantity for {cart_item.item.name}")

                OrderItem.objects.create(
                    order=order,
                    menu_item=cart_item.item,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.item.price,
                    special_requests=cart_item.special_requests or ''
                )

            cart.completed = True
            cart.save()

            # Notifications
            if is_rush:
                Notification.objects.create(
                    message=f"🚨 RUSH order #{order.id} placed for Table {table.table_number} in Room {table.room.name}!",
                    type='order',
                    order=order,
                    metadata={'order_id': order.id}
                )

            Notification.objects.create(
                message=f"New order #{order.id} placed for Table {table.table_number} in Room {table.room.name}!",
                type='order',
                order=order,
                metadata={'order_id': order.id}
            )

            # Update table status & current_order to latest order from this session
            table.current_order = order
            table.status = 'OCCUPIED'
            table.save()

            request.session['order_id'] = order.id
            messages.success(request, f"Order #{order.id} has been placed successfully!")
            return redirect('order_detail', order_id=order.id)

    except Table.DoesNotExist:
        messages.error(request, f"Table {table_number} not found in room {room_number}")
        return redirect('cart')
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('cart')
    except Exception as e:
        messages.error(request, f"Error placing order: {str(e)}")
        return redirect('cart')


def my_orders(request):
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key
    orders = Order.objects.filter(session_key=session_key).order_by('-created_at')

    total_orders = orders.count()
    total_items = sum(order.items.count() for order in orders)
    total_amount = sum(order.total_amount for order in orders)

    return render(request, 'website/my_orders.html', {
        'orders': orders,
        'total_orders': total_orders,
        'total_items': total_items,
        'total_amount': total_amount,
        'page': 'Order History'
    })

def vip_my_orders(request):
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    # Filter only VIP orders for this session
    orders = Order.objects.filter(
        session_key=session_key,
        order_type='vip'
    ).order_by('-created_at')

    total_orders = orders.count()
    total_items = sum(order.items.count() for order in orders)
    total_amount = sum(order.total_amount for order in orders)

    return render(request, 'website/vip/my_orders.html', {
        'orders': orders,
        'total_orders': total_orders,
        'total_items': total_items,
        'total_amount': total_amount,
        'page': 'Vip Order History'
    })


def get_current_order(request, order_type='normal', include_paid=False):
    session_key = 'order_id' if order_type == 'normal' else 'order_id'
    
    order_id = request.session.get(session_key)

    if not order_id:
        return None

    query = Order.objects.filter(id=order_id, order_type=order_type)
    
    if not include_paid:
        query = query.filter(is_paid=False)

    return query.first()

from decimal import Decimal

def order_detail(request, order_id):
    try:
        order = Order.objects.get(id=order_id, order_type='normal')
        
        # Recalculate to ensure consistency (this will update if items changed)
        order.vip_discount = order.calculate_vip_discount()
        order.update_total()
        
        return render(request, 'website/order_detail.html', {
            'order': order,
            'order_items': order.items.all(),
            'original_subtotal': order.original_subtotal,
            'vip_discount': order.vip_discount,
            'subtotal_after_discount': order.subtotal_after_discount,
            'vat': order.vat_amount,
            'service_tax': order.service_charge,
            'grand_total': order.total_amount,
            'is_rush': order.is_rush,
            'page': 'Order Details'
        })
    except Order.DoesNotExist:
        messages.error(request, "Order not found")
        return redirect('cart')

def view_my_order(request):
    order = get_current_order(request, order_type='normal')
    if not order:
        messages.error(request, "No recent order found.")
        return redirect('cart')
    
    # Recalculate to ensure consistency
    order.vip_discount = order.calculate_vip_discount()
    order.update_total()
    
    return render(request, 'website/order_detail.html', {
        'order': order,
        'order_items': order.items.all(),
        'original_subtotal': order.original_subtotal,
        'vip_discount': order.vip_discount,
        'subtotal_after_discount': order.subtotal_after_discount,
        'vat': order.vat_amount,
        'service_tax': order.service_charge,
        'grand_total': order.total_amount,
        'is_rush': order.is_rush,
        'page': 'Your Order'
    })
from django.http import JsonResponse
from orders.models import Order

def get_order_status(request, order_id):
    try:
        order = Order.objects.get(pk=order_id)
        return JsonResponse({
            'status': order.status,
            'status_display': order.get_status_display()
        })
    except Order.DoesNotExist:
        raise Http404("Order not found.")

# vip
@require_POST
def vip_show_confirm_order(request):
    if not request.session.session_key:
        request.session.create()
    
    try:
        cart = get_or_create_cart(request, cart_type='vip')
    except Cart.DoesNotExist:
        messages.error(request, "Your cart is empty")
        return redirect('vip_cart')
    
    if not cart.cartitems.exists():
        messages.error(request, "Your cart is empty")
        return redirect('vip_cart')
    
    # Get all form data from POST request
    customer_name = request.POST.get('customer_name', 'Guest')
    table_number = request.POST.get('table_number', '1')
    room_number = request.POST.get('room_number', '')
    special_requests = request.POST.get('special_requests', '')
    is_rush = request.POST.get('rush_order', 'false') == 'true'
    room_number = request.POST.get('room_number', '')
    room = None
    is_vip_room = False

    if room_number:
        try:
            room = Room.objects.get(name=room_number)
            is_vip_room = (room.room_type == 'VIP')
        except Room.DoesNotExist:
            is_vip_room = False


    # Calculate taxes
    subtotal = cart.total_price
    
    # ✅ Change service charge based on rush
    service_charge_percent = Decimal('0.25') if is_rush else Decimal('0.20')

    
    # ✅ Discount Logic
    if subtotal < 1000:
        discount_percent = Decimal('0.00')
    elif subtotal <= 3000:
        discount_percent = Decimal('0.03')
    elif subtotal <= 6000:
        discount_percent = Decimal('0.06')
    else:
        discount_percent = Decimal('0.10')

    discount_amount = subtotal * discount_percent
    subtotal_after_discount = subtotal - discount_amount

    vat_amount = subtotal_after_discount * Decimal('0.13')
    service_tax = subtotal_after_discount * service_charge_percent

    total_with_tax = subtotal_after_discount + vat_amount + service_tax


    # Prepare order items data
    order_items = []
    for item in cart.cartitems.select_related('item').all():
        order_items.append({
            'name': item.item.name,
            'quantity': item.quantity,
            'price': item.item.price,
            'subtotal': item.item.price * item.quantity,
            'image': item.item.image.url if item.item.image else None
        })

    return render(request, 'website/vip/confirm_order.html', {
        'cart': cart,
        'order_items': order_items,
        'customer_name': customer_name,
        'table_number': table_number,
        'room_number': room_number,
        'special_requests': special_requests,
        'is_rush': is_rush,
        'subtotal': subtotal,
        'discount_percent': int(discount_percent * 100),
        'discount_amount': discount_amount,
        'subtotal_after_discount': subtotal_after_discount,
        'vat_amount': vat_amount,
        'is_vip_room': is_vip_room,
        'service_tax': service_tax,
        'total_with_tax': total_with_tax,
        'total_quantity': sum(item.quantity for item in cart.cartitems.all()),
        'service_charge_percent': int(service_charge_percent * 100)  # Optional: for displaying 10 or 15 in template
    })

@require_POST
def vip_process_order(request):
    if not request.session.session_key:
        request.session.create()

    try:
        cart = get_or_create_cart(request, cart_type='vip')
    except Cart.DoesNotExist:
        messages.error(request, "Your cart is empty")
        return redirect('vip_cart')

    if not cart.cartitems.exists():
        messages.error(request, "Your cart is empty")
        return redirect('vip_cart')

    try:
        with transaction.atomic():
            customer_name = request.POST.get('customer_name')
            table_number = request.POST.get('table_number')
            room_number = request.POST.get('room_number', '')
            special_requests = request.POST.get('special_requests', '')
            is_rush = request.POST.get('is_rush', 'false') == 'true'
            session_key = request.session.session_key

            if not room_number:
                raise ValueError("Room number is required to select a table")

            table = Table.objects.get(table_number=table_number, room__name=room_number)

            # Handle table occupancy like in normal process_order
            if table.status != 'AVAILABLE':
                active_order_for_table = Order.objects.filter(
                    table=table,
                    status__in=['PENDING', 'CONFIRMED', 'PREPARING', 'READY', 'SERVED']
                ).first()

                if active_order_for_table:
                    if active_order_for_table.session_key != session_key:
                        raise ValueError(f"Table {table_number} is currently occupied by another customer.")
                    # else: continue if same session

            # Pricing and discounts
            subtotal = cart.total_price

            if subtotal < 1000:
                vip_discount_percent = Decimal('0.00')
            elif subtotal <= 3000:
                vip_discount_percent = Decimal('0.03')
            elif subtotal <= 6000:
                vip_discount_percent = Decimal('0.06')
            else:
                vip_discount_percent = Decimal('0.10')

            discount_amount = subtotal * vip_discount_percent
            subtotal_after_discount = subtotal - discount_amount

            vat = subtotal_after_discount * Decimal('0.13')
            service_charge_percent = Decimal('0.25') if is_rush else Decimal('0.20')
            service_charge = subtotal_after_discount * service_charge_percent

            total_amount = subtotal_after_discount + vat + service_charge

            # Create order
            order = Order.objects.create(
                table=table,
                customer_name=customer_name,
                special_requests=special_requests,
                total_amount=total_amount,
                vip_discount=discount_amount,
                is_rush=is_rush,
                order_type='vip',
                status='PENDING',
                session_key=session_key  # Match session for this VIP order
            )

            for cart_item in cart.cartitems.select_related('item').all():
                if not cart_item.item.decrease_quantity(cart_item.quantity):
                    raise ValueError(f"Insufficient quantity for {cart_item.item.name}")

                OrderItem.objects.create(
                    order=order,
                    menu_item=cart_item.item,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.item.price,
                    special_requests=cart_item.special_requests or ''
                )

            cart.completed = True
            cart.save()

            # Notifications
            if is_rush:
                Notification.objects.create(
                    message=f"🚨 RUSH + VIP order #{order.id} placed for Table {table.table_number} in Room {table.room.name}!",
                    type='order',
                    order=order,
                    metadata={'order_id': order.id}
                )

            Notification.objects.create(
                message=f"New VIP order #{order.id} placed for Table {table.table_number} in Room {table.room.name}!",
                type='order',
                order=order,
                metadata={'order_id': order.id}
            )

            # Update table status and link order
            table.current_order = order
            table.status = 'OCCUPIED'
            table.save()

            request.session['vip_order_id'] = order.id
            messages.success(request, f"Order #{order.id} has been placed successfully!")
            return redirect('vip_order_detail', order_id=order.id)

    except Table.DoesNotExist:
        messages.error(request, f"Table {table_number} not found in room {room_number}")
        return redirect('vip_cart')
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('vip_cart')
    except Exception as e:
        messages.error(request, f"Error placing order: {str(e)}")
        return redirect('vip_cart')

def vip_get_current_order(request, order_type='vip',include_paid=False):
    session_key = 'vip_order_id' if order_type == 'vip' else 'order_id'
    order_id = request.session.get(session_key)
    if not order_id:
        return None

    query = Order.objects.filter(id=order_id, order_type=order_type)
    
    if not include_paid:
        query = query.filter(is_paid=False)

    return query.first()


from django.shortcuts import get_object_or_404
def vip_order_detail(request, order_id):
    try:
        order = Order.objects.get(id=order_id, order_type='vip')
        
        # Recalculate to ensure consistency
        order.vip_discount = order.calculate_vip_discount()
        order.update_total()
        
        return render(request, 'website/vip/order_detail.html', {
            'order': order,
            'order_items': order.items.all(),
            'original_subtotal': order.original_subtotal,
            'vip_discount': order.vip_discount,
            'subtotal_after_discount': order.subtotal_after_discount,
            'vat': order.vat_amount,
            'service_tax': order.service_charge,
            'grand_total': order.total_amount,
            'is_rush': order.is_rush,
            'page': 'Order Details'
        })
    except Order.DoesNotExist:
        messages.error(request, "Order not found")
        return redirect('vip_cart')

def vip_view_my_order(request):
    order = vip_get_current_order(request)
    if not order:
        messages.error(request, "No recent order found.")
        return redirect('vip_cart')
    
    # Recalculate to ensure consistency
    order.vip_discount = order.calculate_vip_discount()
    order.update_total()
    
    return render(request, 'website/vip/order_detail.html', {
        'order': order,
        'order_items': order.items.all(),
        'original_subtotal': order.original_subtotal,
        'vip_discount': order.vip_discount,
        'subtotal_after_discount': order.subtotal_after_discount,
        'vat': order.vat_amount,
        'service_tax': order.service_charge,
        'grand_total': order.total_amount,
        'is_rush': order.is_rush,
        'page': 'Your Order'
    })

def vip_get_order_status(request, order_id):
    try:
        order = Order.objects.get(pk=order_id)
        return JsonResponse({
            'status': order.status,
            'status_display': order. get_status_display()
        })
    except Order.DoesNotExist:
        raise Http404("Order not found.")
    

# payment .. 
from django.shortcuts import render, get_object_or_404
from orders.models import Order
from django.http import JsonResponse


import random
import string

def generate_transaction_id():
    random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    return f"transaction_{random_part}"

def khalti_payment_request(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    amount_paisa = int(order.total_amount * 100)

    data = {
        'khalti_public_key': 'mock-public-key',  # No real public key needed now
        'amount_paisa': amount_paisa,
        'order_id': order.id,
    }
    return JsonResponse(data)



from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
import json
from orders.models import Order
from payments.models import Payment
@csrf_exempt
def khalti_payment_verify(request):
    if request.method == "POST":
        data = json.loads(request.body)
        order_id = data.get("order_id")
        token = data.get("token")
        amount = data.get("amount")

        order = get_object_or_404(Order, id=order_id)

        if token == "fake-token-123456":
            # Mark order as paid
            order.is_paid = True
            order.save()

            # Create Payment entry
            transaction_id = generate_transaction_id()
            payment = Payment.objects.create(
                order=order,
                method='MOBILE',
                amount=amount / 100,
                transaction_id=transaction_id,
                status='COMPLETED'
            )

            # Create Notification 
            Notification.objects.create(
                type='payment',
                message=f"Payment of Rs. {payment.amount} completed for Order #{order.id}.",
                order=order,
                payment=payment,
                metadata={
                    'order_id': order.id,
                    'amount': str(payment.amount),
                    'method': 'Khalti',
                    'transaction_id': transaction_id
                }
            )

            return JsonResponse({"status": "success"})
        else:
            return JsonResponse({"status": "fail"})

    return JsonResponse({"status": "invalid"}, status=400)


@csrf_exempt
def khalti_payment_verify_vip(request):
    if request.method == "POST":
        data = json.loads(request.body)
        order_id = data.get("order_id")
        token = data.get("token")
        amount = data.get("amount")

        order = get_object_or_404(Order, id=order_id)

        if token == "fake-token-123456":
            # Mark order as paid
            order.is_paid = True
            order.save()

            # Create Payment entry
            transaction_id = generate_transaction_id()
            payment = Payment.objects.create(
                order=order,
                method='MOBILE',
                amount=amount / 100,
                transaction_id=transaction_id,
                status='COMPLETED'
            )

            # Create Notification 
            Notification.objects.create(
                type='payment',
                message=f"Payment of Rs. {payment.amount} completed for Order #{order.id}.",
                order=order,
                payment=payment,
                metadata={
                    'order_id': order.id,
                    'amount': str(payment.amount),
                    'method': 'MOBILE',
                    'transaction_id': transaction_id
                }
            )

            return JsonResponse({"status": "success"})
        else:
            return JsonResponse({"status": "fail"})

    return JsonResponse({"status": "invalid"}, status=400)


from django.contrib.messages import get_messages
from django.http import JsonResponse

# views.py
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from user_staff.models import Notification


@require_GET
def order_status_notifications_view(request):
    # Get session key (create if doesn't exist)
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    
    # Get only order status notifications for this session
    notifications = Notification.objects.filter(
        session_key=session_key,
        type='order_Status',
        is_deleted=False
    ).order_by('-created_at')
    
    # Count unread notifications
    unread_count = notifications.filter(is_read=False).count()
    
    # Mark all as read when viewing the page
    if notifications.filter(is_read=False).exists():
        notifications.filter(is_read=False).update(is_read=True)
    
    context = {
        'notifications': notifications,
        'unread_notification_count': unread_count,
        'page': 'Order Notifications'
    }
    
    return render(request, 'website/order_status_notification.html', context)

from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone

@require_GET
@csrf_exempt
def fetch_unread_notifications(request):
    try:
        # Ensure session exists, or return no session response
        if not request.session.session_key:
            return JsonResponse({
                'status': 'no_session',
                'unread_count': 0,
                'notifications': []
            })

        # Query notifications by session_key only
        notifications = Notification.objects.filter(
            session_key=request.session.session_key,
            is_read=False,
            is_deleted=False
        )

        # Get notification data for last 10 notifications
        notifications_data = list(notifications.order_by('-created_at')[:10].values(
            'id',
            'message',
            'type',
            'created_at',
            'metadata'
        ))

        # Debug print to console/log
        print(f"Returning unread count (session only): {notifications.count()}")
        print(f"Sample notifications: {list(notifications.values('id', 'message')[:2])}")

        return JsonResponse({
            'status': 'success',
            'unread_count': len(notifications_data),
            'notifications': notifications_data,
            'last_updated': timezone.now().isoformat()
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'unread_count': 0,
            'notifications': []
        }, status=500)


@require_GET
def vip_order_status_notifications_view(request):
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key

    # Filter only VIP order status notifications
    notifications = Notification.objects.filter(
        session_key=session_key,
        type='order_Status',
        is_deleted=False,
        order__order_type='vip'
    ).order_by('-created_at')

    unread_count = notifications.filter(is_read=False).count()

    if unread_count > 0:
        notifications.filter(is_read=False).update(is_read=True)

    context = {
        'notifications': notifications,
        'unread_notification_count': unread_count,
        'page': 'Order Notifications'
    }

    return render(request, 'website/vip/order_status_notification.html', context)




@require_GET
@csrf_exempt
def vip_fetch_unread_notifications(request):
    try:
        if not request.session.session_key:
            return JsonResponse({
                'status': 'no_session',
                'unread_count': 0,
                'notifications': []
            })

        # Filter only unread, not deleted VIP notifications
        notifications = Notification.objects.filter(
            session_key=request.session.session_key,
            is_read=False,
            is_deleted=False,
            order__order_type='vip'
        )

        notifications_data = list(notifications.order_by('-created_at')[:10].values(
            'id',
            'message',
            'type',
            'created_at',
            'metadata'
        ))

        print(f"Returning unread count (session only): {notifications.count()}")
        print(f"Sample notifications: {list(notifications.values('id', 'message')[:2])}")

        return JsonResponse({
            'status': 'success',
            'unread_count': len(notifications_data),
            'notifications': notifications_data,
            'last_updated': timezone.now().isoformat()
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'unread_count': 0,
            'notifications': []
        }, status=500)
