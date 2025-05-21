from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import MenuItem, Cart,CartItem
from categories.models import Category
from django.urls import reverse
from django.http import JsonResponse
import json
import uuid
from django.contrib import messages


def menu_for_customers(request):
    search_query = request.GET.get('search', '').strip()
    is_search = bool(search_query)

    # Base queryset
    menu_items = MenuItem.objects.filter(is_available=True)
    
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
        'special_items': special_items,
        'categories': categories,
        'current_sort': sort_by,
        'current_category': category_id,
        'search_term': search_query,
        'is_search': is_search,
        'page': 'Menu'
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

def handle_search(request):
    """Redirect to menu page with search query"""
    search_query = request.GET.get('search', '').strip()
    return redirect(f"{reverse('customer_menu')}?search={search_query}")



def cart(request):
    if not request.session.session_key:
        request.session.create()

    session_id = request.session.session_key

    try:
        cart = Cart.objects.get(session_id=session_id, completed=False)
        cart_items = cart.cartitems.select_related('item')
        subtotal = cart.total_price
        total_quantity = cart.num_of_items
    except Cart.DoesNotExist:
        cart = None
        cart_items = []
        subtotal = 0
        total_quantity = 0

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total_quantity': total_quantity,
        'page': 'Your Cart',
    }

    return render(request, 'website/cart.html', context)


def add_to_cart(request):
    # Load JSON data from request
    data = json.loads(request.body)
    item_id = data.get("id")
    
    try:
        item = MenuItem.objects.get(id=item_id)
        
        # Ensure session exists
        if not request.session.session_key:
            request.session.create()
        
        # Get or create cart
        cart, created = Cart.objects.get_or_create(
            session_id=request.session.session_key,
            completed=False
        )
        
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
    
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Cart, CartItem, MenuItem
from django.shortcuts import get_object_or_404

def get_or_create_cart(request):
    if not request.session.session_key:
        request.session.create()
    cart, _ = Cart.objects.get_or_create(session_id=request.session.session_key, completed=False)
    return cart

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
