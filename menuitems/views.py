
from django.shortcuts import render, redirect,  get_object_or_404
from django.contrib import messages
from .models import MenuItem
from categories.models import Category
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from .decorators import admin_required

@login_required(login_url='/login/')
def available_items(request):
    print("is_superuser:", request.user.is_superuser)
    print("is_staff:", request.user.is_staff)
    print("username:", request.user.username)

    items = MenuItem.objects.all().order_by('category__display_order', 'name')

    if request.user.is_superuser:
        template = 'menuitems/admin/available_items.html'
    elif request.user.is_staff:
        template = 'menuitems/staff/available_items.html'
    else:
        raise PermissionDenied("You do not have access to this page.")

    context = {
        'menu_items': items,
        'page': 'Available Menu Items',
        'current_section': 'Menu / Available Items',
    }
    return render(request, template, context)

@login_required(login_url='/login/')
def view_item(request, id):
    queryset = MenuItem.objects.get(id = id)
    
    
    if request.user.is_superuser:
        template = 'menuitems/admin/view_item.html'
    elif request.user.is_staff:
        template = 'menuitems/staff/view_item.html'
    else:
        raise PermissionDenied("You do not have access to this page.")

    return render(request, template, {
        'page': 'View Menu Item',
        'current_section': 'View-Menu-Item',
        'menu_items':queryset
    })

@login_required(login_url='/login/')
def update_item(request, item_id):
    try:
        menu_item = MenuItem.objects.get(pk=item_id)
    except MenuItem.DoesNotExist:
        messages.error(request, "Menu item not found")
        return redirect('menuitem:available_items')

    
    if request.user.is_superuser:
        template = 'menuitems/admin/update_item.html'
        redirect_to_update = 'menuitem:admin_update_item'
        redirect_to_success = 'menuitem:admin_available_items'
    elif request.user.is_staff:
        template = 'menuitems/staff/update_item.html'
        redirect_to_update = 'menuitem:staff_update_item'
        redirect_to_success = 'menuitem:staff_available_items'
    else:
        raise PermissionDenied("You do not have access to this page.")
    
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
        vip_status = request.POST.get('vip_status', 'REGULAR')  # Get VIP status from form

        # Validation
        if not name or not price or not category_id:
            messages.error(request, "Name, price, and category are required")
            return redirect(redirect_to_update, item_id=item_id)

        try:
            price = float(price)
            if price < 0:
                raise ValueError("Price must be positive")
        except ValueError:
            messages.error(request, "Price must be a valid positive number")
            return redirect(redirect_to_update, item_id=item_id)

        try:
            quantity = int(quantity)
            if quantity < 0:
                raise ValueError("Quantity must be non-negative")
        except ValueError:
            messages.error(request, "Quantity must be a valid non-negative integer")
            return redirect(redirect_to_update, item_id=item_id)

        try:
            preparation_time = int(preparation_time)
            if preparation_time <= 0:
                raise ValueError("Preparation time must be positive")
        except ValueError:
            messages.error(request, "Preparation time must be a valid positive integer")
            return redirect(redirect_to_update, item_id=item_id)

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            messages.error(request, "Selected category does not exist")
            return redirect(redirect_to_update, item_id=item_id)

        # Check if name already exists (excluding current item)
        if MenuItem.objects.filter(name=name).exclude(pk=item_id).exists():
            messages.error(request, f"A menu item with name '{name}' already exists")
            return redirect(redirect_to_update, item_id=item_id)

        try:
            # Update fields
            menu_item.name = name
            menu_item.description = description
            menu_item.price = price
            menu_item.category = category
            menu_item.is_available = is_available
            menu_item.quantity = quantity
            menu_item.preparation_time = preparation_time
            menu_item.vip_status = vip_status  # Set VIP status
            
            # Only update image if a new one was provided
            if image:
                menu_item.image = image
            
            menu_item.save()
            
            messages.success(request, "Menu item updated successfully!")
            return redirect(redirect_to_success)
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect(redirect_to_update, item_id=item_id)

    categories = Category.objects.filter(is_active=True).order_by('display_order')
    return render(request, template, {
        'menu_item': menu_item,
        'categories': categories,
        'vip_status_choices': MenuItem.VIP_STATUS_CHOICES,  # Pass choices to template
        'page': 'Update Menu Item',
        'current_section': 'Menu / Update Item',
    })

@login_required(login_url='/login/')
def add_item(request):
    
    if request.user.is_superuser:
        template = 'menuitems/admin/add_item.html'
        redirect_to_add = 'menuitem:admin_add_item'
        redirect_to_success = 'menuitem:admin_available_items'
    elif request.user.is_staff:
        template = 'menuitems/staff/add_item.html'
        redirect_to_add = 'menuitem:staff_add_item'
        redirect_to_success = 'menuitem:staff_available_items'
    else:
        raise PermissionDenied()

    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        price = request.POST.get('price')
        category_id = request.POST.get('category')
        quantity = request.POST.get('quantity', 0)
        vip_status = request.POST.get('vip_status', 'REGULAR')  # Get VIP status from form
        
        try:
            quantity = int(quantity)
            if quantity < 0:
                raise ValueError("Quantity must be non-negative")
        except ValueError:
            messages.error(request, "Quantity must be a valid non-negative integer")
            return redirect(redirect_to_add)

        is_available = quantity > 0 and request.POST.get('is_available') == 'on'
        preparation_time = request.POST.get('preparation_time', 15)
        image = request.FILES.get('image')

        # Validation
        if not name or not price or not category_id:
            messages.error(request, "Name, price, and category are required")
            return redirect(redirect_to_add)

        try:
            price = float(price)
            if price < 0:
                raise ValueError("Price must be a positive number")
        except ValueError:
            messages.error(request, "Price must be a valid positive number")
            return redirect(redirect_to_add)

        try:
            quantity = int(quantity)
            if quantity < 0:
                raise ValueError("Quantity must be non-negative")
        except ValueError:
            messages.error(request, "Quantity must be a valid non-negative integer")
            return redirect(redirect_to_add)

        try:
            preparation_time = int(preparation_time)
            if preparation_time <= 0:
                raise ValueError("Preparation time must be positive")
        except ValueError:
            messages.error(request, "Preparation time must be a valid positive integer")
            return redirect(redirect_to_add)

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            messages.error(request, "Selected category does not exist")
            return redirect(redirect_to_add)

        # Check if name already exists
        if MenuItem.objects.filter(name=name).exists():
            messages.error(request, f"A menu item with name '{name}' already exists")
            return redirect(redirect_to_add)

        try:
            # Create the menu item with VIP status
            menu_item = MenuItem(
                name=name,
                description=description,
                price=price,
                category=category,
                is_available=is_available,
                quantity=quantity,
                preparation_time=preparation_time,
                image=image,
                vip_status=vip_status  # Set VIP status
            )
            menu_item.save()
            
            messages.success(request, "Menu item added successfully!")
            return redirect(redirect_to_success)
        except IntegrityError as e:
            messages.error(request, f"Database error: {str(e)}")
            return redirect(redirect_to_add)
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect(redirect_to_add)

    categories = Category.objects.filter(is_active=True).order_by('display_order')
    return render(request, template, {
        'categories': categories,
        'vip_status_choices': MenuItem.VIP_STATUS_CHOICES,  # Pass choices to template
        'page': 'Add new Menu Item',
        'current_section': 'Menu / Add new Item',
    })

@login_required(login_url='/login/')
def delete_item(request, id):
    item = get_object_or_404(MenuItem, id=id)
    
    if request.user.is_superuser:
        template = 'menuitems/admin/confirm_delete.html'
        redirect_to_success = 'menuitem:admin_available_items'
    elif request.user.is_staff:
        template = 'menuitems/staff/confirm_delete.html'
        redirect_to_success = 'menuitem:staff_available_items'
    else:
        raise PermissionDenied("You do not have access to this page.")
    
    if request.method == "POST":
        item.delete()
        messages.success(request, "Menu item deleted successfully!")
        return redirect(redirect_to_success)  # Replace with your actual redirect URL name

    return render(request, template, {
        'page': 'Delete Menu Item',
        'item': item,
        'current_section': 'Menu / Delete Item',
    })
from django.views.decorators.http import require_POST
@admin_required
@require_POST
def clear_all_items(request):
    MenuItem.objects.all().delete()
    messages.success(request, "All menu items have been deleted.")
    return redirect('admin_available_items')
