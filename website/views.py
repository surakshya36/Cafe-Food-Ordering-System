from django.shortcuts import render
from .models import MenuItem

def menu_for_customers(request):
    menu_items = MenuItem.objects.filter(is_available=True).select_related('category')
    return render(request, 'website/menu_lists.html', {
        'menu_items': menu_items,
        'page': 'Menu'
    })


def menu_view(request):
    menu_items = MenuItem.objects.filter(is_available=True)
    return render(request, 'website/menu_item_card.html', {
        'menu_items': menu_items
    })