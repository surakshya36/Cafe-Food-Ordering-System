from django.shortcuts import render
from .models import MenuItem
from categories.models import Category
def menu_for_customers(request):
    search_query = request.GET.get('search')
    is_search = bool(search_query and search_query.strip())

    if is_search:
        menu_items = MenuItem.objects.filter(
            is_available=True,
            name__icontains=search_query.strip()
        ).select_related('category')

        # Skip loading special items
        special_items = None
    else:
        special_items = MenuItem.objects.filter(
            is_available=True,
            vip_status='TODAYS_SPECIAL'
        ).select_related('category')

        menu_items = MenuItem.objects.filter(
            is_available=True,
            vip_status__in=['REGULAR', 'TODAYS_SPECIAL']
        ).select_related('category')

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
        'page': 'Menu',
        'search_term': search_query,
        'is_search': is_search
    })

def menu_view(request):
    menu_items = MenuItem.objects.filter(is_available=True).select_related('category')
    categories = Category.objects.all()
    
    # Similar sorting logic as above
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
    
    return render(request, 'website/menu_item_card.html', {
        'menu_items': menu_items,
        'categories': categories,
        'current_sort': sort_by,
        'current_category': category_id
    })

