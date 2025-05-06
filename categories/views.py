from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import IntegrityError
from .models import Category

def display_categories(request):
    categories = Category.objects.all().order_by('display_order', 'name')
    return render(request, 'categories/display_categories.html', {
        'page': 'Available Categories',
        'current_section': 'Categories',
        'categories': categories
    })

def add_category(request):
    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        display_order = request.POST.get('display_order', 0)
        is_active = request.POST.get('is_active') == 'on'
        category_type = request.POST.get('category_type', 'NORMAL')

        # Validation
        if not name:
            messages.error(request, "Category name is required")
            return redirect('add_category')
            
        try:
            display_order = int(display_order)
            if display_order < 0:
                messages.error(request, "Display order must be a positive number")
                return redirect('add_category')
                
            # Check if name already exists
            if Category.objects.filter(name=name).exists():
                messages.error(request, f"A category with name '{name}' already exists")
                return redirect('add_category')
                
            # Check if display order already exists
            if Category.objects.filter(display_order=display_order).exists():
                messages.warning(request, f"Display order {display_order} is already taken")
                return redirect('add_category')

            Category.objects.create(
                name=name,
                description=description,
                display_order=display_order,
                is_active=is_active,
                category_type=category_type
            )
            messages.success(request, "Category added successfully!")
            return redirect('available_categories')
            
        except ValueError:
            messages.error(request, "Display order must be a valid number")
            return redirect('add_category')
        except IntegrityError as e:
            messages.error(request, f"Database error: {str(e)}")
            return redirect('add_category')
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('add_category')
    
    return render(request, 'categories/add_category.html', {
        'page': 'Add new Category',
        'current_section': 'Categories / Add new Category',
        'category_types': Category.CATEGORY_TYPES
    })

def update_category(request, id):
    category = get_object_or_404(Category, id=id)
    
    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        display_order = request.POST.get('display_order', 0)
        is_active = request.POST.get('is_active') == 'on'
        category_type = request.POST.get('category_type', 'NORMAL')

        # Basic validation
        if not name:
            messages.error(request, "Category name is required")
            return redirect('update_category', id=id)
            
        try:
            display_order = int(display_order)
            if display_order < 0:
                messages.error(request, "Display order must be a positive number")
                return redirect('update_category', id=id)
        except ValueError:
            messages.error(request, "Display order must be a valid number")
            return redirect('update_category', id=id)

        # Check for duplicate name (excluding current category)
        if Category.objects.filter(name=name).exclude(id=id).exists():
            messages.error(request, f"A category with name '{name}' already exists")
            return redirect('update_category', id=id)
            
        # Check for duplicate display order (excluding current category)
        if Category.objects.filter(display_order=display_order).exclude(id=id).exists():
            messages.warning(request, f"Display order {display_order} is already taken")
            return redirect('update_category', id=id)

        # Update the category
        category.name = name
        category.description = description
        category.display_order = display_order
        category.is_active = is_active
        category.category_type = category_type
        category.save()
        
        messages.success(request, "Category updated successfully!")
        return redirect('available_categories')

    return render(request, 'categories/update_category.html', {
        'page': 'Update Category',
        'category': category,
        'current_section': 'Categories / Update Category',
        'category_types': Category.CATEGORY_TYPES
    })

# def view_category(request, id):
#     category = get_object_or_404(Category, id=id)
#     menu_items = category.menu_items.all()  # Using the related_name from MenuItem model
    
#     return render(request, 'categories/view_category.html', {
#         'page': 'View Category',
#         'category': category,
#         'menu_items': menu_items,
#         'current_section': 'Categories / View Category'
#     })

def delete_category(request, id):
    category = get_object_or_404(Category, id=id)
    
    if request.method == 'POST':
        try:
            category_name = category.name
            # Check if category has any menu items
            if category.menu_items.exists():
                messages.error(request, f"Cannot delete '{category_name}' because it has menu items assigned")
                return redirect('available_categories')
                
            category.delete()
            messages.success(request, f"Category '{category_name}' deleted successfully!")
        except Exception as e:
            messages.error(request, f"Error deleting category: {str(e)}")
        
        return redirect('display_categories')
    
    return render(request, 'categories/confirm_delete.html', {
        'page': 'Confirm Delete',
        'category': category,
        'current_section': 'Categories / Delete Category'
    })