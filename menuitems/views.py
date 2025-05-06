
from django.shortcuts import render, redirect,  get_object_or_404
from django.contrib import messages
from .models import MenuItem
from categories.models import Category
from django.db import IntegrityError

def available_items(request):
    items = MenuItem.objects.all().order_by('category__display_order', 'name')
    return render(request, 'menuitems/available_items.html', {
        'menu_items': items,
        'page': 'Available Menu items',
        'current_section': 'Menu-Items',
    })

def view_item(request, id):
    queryset = MenuItem.objects.get(id = id)
    
    return render(request, 'menuitems/view_item.html', {
        'page': 'View Menu Item',
        'current_section': 'View-Menu-Item',
        'menu_items':queryset
    })

def update_item(request, item_id):
    try:
        menu_item = MenuItem.objects.get(pk=item_id)
    except MenuItem.DoesNotExist:
        messages.error(request, "Menu item not found")
        return redirect('available_items')

    if request.method == "POST":
        # Get form data
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        price = request.POST.get('price')
        category_id = request.POST.get('category')
        is_available = request.POST.get('is_available') == 'on'
        quantity = request.POST.get('quantity', 0)
        preparation_time = request.POST.get('preparation_time', 15)
        image = request.FILES.get('image')

        # Validation
        if not name or not price or not category_id:
            messages.error(request, "Name, price, and category are required")
            return redirect('update_item', item_id=item_id)

        try:
            price = float(price)
            if price < 0:
                raise ValueError("Price must be positive")
        except ValueError:
            messages.error(request, "Price must be a valid positive number")
            return redirect('update_item', item_id=item_id)

        try:
            quantity = int(quantity)
            if quantity < 0:
                raise ValueError("Quantity must be non-negative")
        except ValueError:
            messages.error(request, "Quantity must be a valid non-negative integer")
            return redirect('update_item', item_id=item_id)

        try:
            preparation_time = int(preparation_time)
            if preparation_time <= 0:
                raise ValueError("Preparation time must be positive")
        except ValueError:
            messages.error(request, "Preparation time must be a valid positive integer")
            return redirect('update_item', item_id=item_id)

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            messages.error(request, "Selected category does not exist")
            return redirect('update_item', item_id=item_id)

        # Check if name already exists (excluding current item)
        if MenuItem.objects.filter(name=name).exclude(pk=item_id).exists():
            messages.error(request, f"A menu item with name '{name}' already exists")
            return redirect('update_item', item_id=item_id)

        try:
            # Update fields
            menu_item.name = name
            menu_item.description = description
            menu_item.price = price
            menu_item.category = category
            menu_item.is_available = is_available
            menu_item.quantity = quantity
            menu_item.preparation_time = preparation_time
            
            # Only update image if a new one was provided
            if image:
                menu_item.image = image
            
            # VIP status will be automatically updated in save() method
            menu_item.save()
            
            messages.success(request, "Menu item updated successfully!")
            return redirect('available_items')
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('update_item', item_id=item_id)

    categories = Category.objects.filter(is_active=True).order_by('display_order')
    return render(request, 'menuitems/update_item.html', {
        'menu_item': menu_item,
        'categories': categories,
        'page': 'Update Menu Item',
        'current_section': 'Menu / Update Item',
    })

def delete_item(request, id):
    item = get_object_or_404(MenuItem, id=id)

    if request.method == "POST":
        item.delete()
        return redirect('available_items')  # Replace with your actual redirect URL name

    return render(request, 'menuitems/confirm_delete.html', {
        'page': 'Delete Menu Item',
        'item': item,
        'current_section': 'Menu / Delete Item',
    })

def add_item(request):
    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        price = request.POST.get('price')
        category_id = request.POST.get('category')
        is_available = request.POST.get('is_available') == 'on'
        quantity = request.POST.get('quantity', 0)
        preparation_time = request.POST.get('preparation_time', 15)
        image = request.FILES.get('image')

        # Validation (keep your existing validation code)
        if not name or not price or not category_id:
            messages.error(request, "Name, price, and category are required")
            return redirect('add_item')

        try:
            price = float(price)
            if price < 0:
                raise ValueError("Price must be a positive number")
        except ValueError:
            messages.error(request, "Price must be a valid positive number")
            return redirect('add_item')

        try:
            quantity = int(quantity)
            if quantity < 0:
                raise ValueError("Quantity must be non-negative")
        except ValueError:
            messages.error(request, "Quantity must be a valid non-negative integer")
            return redirect('add_item')

        try:
            preparation_time = int(preparation_time)
            if preparation_time <= 0:
                raise ValueError("Preparation time must be positive")
        except ValueError:
            messages.error(request, "Preparation time must be a valid positive integer")
            return redirect('add_item')

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            messages.error(request, "Selected category does not exist")
            return redirect('add_item')

        # Check if name already exists
        if MenuItem.objects.filter(name=name).exists():
            messages.error(request, f"A menu item with name '{name}' already exists")
            return redirect('add_item')

        try:
            # Create the menu item - vip_status will be set automatically in save()
            menu_item = MenuItem(
                name=name,
                description=description,
                price=price,
                category=category,
                is_available=is_available,
                quantity=quantity,
                preparation_time=preparation_time,
                image=image
            )
            # No need to set vip_status here - it will be handled in save()
            menu_item.save()
            
            messages.success(request, "Menu item added successfully!")
            return redirect('available_items')
        except IntegrityError as e:
            messages.error(request, f"Database error: {str(e)}")
            return redirect('add_item')
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('add_item')

    categories = Category.objects.filter(is_active=True).order_by('display_order')
    return render(request, 'menuitems/add_item.html', {
        'categories': categories,
        'page': 'Add new Menu Item',
        'current_section': 'Menu / Add new Item',
    })