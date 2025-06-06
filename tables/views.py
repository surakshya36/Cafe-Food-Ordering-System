from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Room, Table
from django.urls import reverse
from .decorators import admin_required, staff_required

# rooms
@admin_required
def available_rooms(request):
    rooms = Room.objects.filter(is_active=True).order_by('room_type', 'name')
    return render(request, 'tables/admin/rooms/available_rooms.html', {
        'rooms': rooms,
        'page': 'Available Rooms',
        'current_section': 'Rooms',
    })

@admin_required
def add_room(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        room_type = request.POST.get('room_type')
        description = request.POST.get('description', '')
        capacity = request.POST.get('capacity')
        
        # Validation 
        if not name or not room_type or not capacity:
            messages.error(request, "Name, type, and capacity are required")
            return redirect('table:add_room')
        
        try:
            capacity = int(capacity)
            if capacity <= 0:
                raise ValueError("Capacity must be positive")
        except ValueError:
            messages.error(request, "Capacity must be a valid positive number")
            return redirect('table:add_room')
        
        try:
            Room.objects.create(
                name=name,
                room_type=room_type,
                description=description,
                capacity=capacity
            )
            messages.success(request, "Room added successfully!")
            return redirect('table:available_rooms')
        except Exception as e:
            messages.error(request, f"Error creating room: {str(e)}")
            return redirect('table:add_room')
    
    return render(request, 'tables/admin/rooms/add_room.html', {
        'page': 'Add New Room',
        'current_section': 'Rooms / Add',
    })

@admin_required
def edit_room(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        room_type = request.POST.get('room_type')
        description = request.POST.get('description', '')
        capacity = request.POST.get('capacity')
        is_active = request.POST.get('is_active') == 'on'
        
        # Validation
        if not name or not room_type or not capacity:
            messages.error(request, "Name, type, and capacity are required")
            return redirect('table:edit_room', room_id=room_id)
        
        try:
            capacity = int(capacity)
            if capacity <= 0:
                raise ValueError("Capacity must be positive")
        except ValueError:
            messages.error(request, "Capacity must be a valid positive number")
            return redirect('table:edit_room', room_id=room_id)
        
        try:
            room.name = name
            room.room_type = room_type
            room.description = description
            room.capacity = capacity
            room.is_active = is_active
            room.save()
            messages.success(request, "Room updated successfully!")
            return redirect('table:available_rooms')
        except Exception as e:
            messages.error(request, f"Error updating room: {str(e)}")
            return redirect('table:edit_room', room_id=room_id)
    
    return render(request, 'tables/admin/rooms/edit_room.html', {
        'room': room,
        'page': 'Edit Room',
        'current_section': 'Rooms / Edit',
    })

@admin_required
def delete_room(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    
    if request.method == 'POST':
        try:
            room.delete()
            messages.success(request, "Room deleted successfully!")
        except Exception as e:
            messages.error(request, f"Error deleting room: {str(e)}")
        return redirect('table:available_rooms')
    
    return render(request, 'tables/admin/rooms/confirm_delete.html', {
        'object': room,
        'type': 'room',
        'page': 'Confirm Delete',
        'current_section': 'Rooms / Delete',
    })


# tables
@admin_required
def available_tables(request):
    tables = Table.objects.select_related('room').order_by('room', 'table_number')
    return render(request, 'tables/admin/tables/available_tables.html', {
        'tables': tables,
        'page': 'Available Tables',
        'current_section': 'Tables',
    })
@admin_required
def add_table(request):
    rooms = Room.objects.filter(is_active=True)

    if request.method == 'POST':
        room_id = request.POST.get('room')
        table_number = request.POST.get('table_number')
        seats = request.POST.get('seats')
        status = request.POST.get('status', 'AVAILABLE')
        x_position = request.POST.get('x_position')
        y_position = request.POST.get('y_position')

        # Basic validation
        if not room_id or not table_number or not seats:
            messages.error(request, "Room, table number, and seats are required")
            return redirect('table:add_table')

        try:
            room = Room.objects.get(pk=room_id)

            # Check room capacity before adding new table
            current_table_count = Table.objects.filter(room=room).count()
            if current_table_count >= room.capacity:
                messages.error(
                    request, 
                    f"This room already has the maximum allowed {room.capacity} tables."
                )
                return redirect('table:add_table')

            # Seats and coordinates validation
            seats = int(seats)
            if seats <= 0:
                raise ValueError("Seats must be a positive number")
            x_pos = float(x_position) if x_position else None
            y_pos = float(y_position) if y_position else None

        except Room.DoesNotExist:
            messages.error(request, "Selected room does not exist")
            return redirect('table:add_table')
        except ValueError:
            messages.error(request, "Seats and positions must be valid numbers")
            return redirect('table:add_table')

        try:
            Table.objects.create(
                room=room,
                table_number=table_number,
                seats=seats,
                status=status,
                x_position=x_pos,
                y_position=y_pos
            )
            messages.success(request, "Table added successfully!")
            return redirect('table:available_tables')
        except Exception as e:
            messages.error(request, f"Error creating table: {str(e)}")
            return redirect('table:add_table')

    return render(request, 'tables/admin/tables/add_table.html', {
        'rooms': rooms,
        'page': 'Add New Table',
        'current_section': 'Tables / Add',
    })


@admin_required
def edit_table(request, table_id):
    table = get_object_or_404(Table, pk=table_id)
    rooms = Room.objects.filter(is_active=True)
    
    if request.method == 'POST':
        room_id = request.POST.get('room')
        table_number = request.POST.get('table_number')
        seats = request.POST.get('seats')
        status = request.POST.get('status')
        x_position = request.POST.get('x_position')
        y_position = request.POST.get('y_position')
        
        # Validation
        if not room_id or not table_number or not seats:
            messages.error(request, "Room, table number, and seats are required")
            return redirect('table:edit_table', table_id=table_id)
        
        try:
            room = Room.objects.get(pk=room_id)
            seats = int(seats)
            if seats <= 0:
                raise ValueError("Seats must be positive")
                
            x_pos = float(x_position) if x_position else None
            y_pos = float(y_position) if y_position else None
        except Room.DoesNotExist:
            messages.error(request, "Selected room does not exist")
            return redirect('table:edit_table', table_id=table_id)
        except ValueError:
            messages.error(request, "Seats must be a valid positive number")
            return redirect('table:edit_table', table_id=table_id)
        
        try:
            table.room = room
            table.table_number = table_number
            table.seats = seats
            table.status = status
            table.x_position = x_pos
            table.y_position = y_pos
            table.save()
            messages.success(request, "Table updated successfully!")
            return redirect('table:available_tables')
        except Exception as e:
            messages.error(request, f"Error updating table: {str(e)}")
            return redirect('table:edit_table', table_id=table_id)
    
    return render(request, 'tables/admin/tables/edit_table.html', {
        'table': table,
        'rooms': rooms,
        'page': 'Edit Table',
        'current_section': 'Tables / Edit',
    })

@admin_required
def delete_table(request, table_id):
    table = get_object_or_404(Table, pk=table_id)
    
    if request.method == 'POST':
        try:
            table.delete()
            messages.success(request, "Table deleted successfully!")
        except Exception as e:
            messages.error(request, f"Error deleting table: {str(e)}")
        return redirect('table:available_tables')
    
    return render(request, 'tables/admin/tables/confirm_delete.html', {
        'object': table,
        'type': 'table',
        'page': 'Confirm Delete',
        'current_section': 'Tables / Delete',
    })

@staff_required
def staff_available_rooms(request):
    rooms = Room.objects.filter(is_active=True).order_by('room_type', 'name')
    return render(request, 'tables/staff/rooms/available_rooms.html', {
        'rooms': rooms,
        'page': 'Available Rooms',
        'current_section': 'Rooms',
    })

@staff_required
def tables_by_room(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    tables = Table.objects.filter(room=room)
    
    return render(request, 'tables/staff/tables/available_tables.html', {
        'room': room,
        'tables': tables,
        'page': f'Tables in {room.name}',
        'current_section': 'Tables by Room',
    })

@staff_required
def table_detail(request, table_id):
    table = get_object_or_404(Table, pk=table_id)
    current_order = table.current_order  # if set via your model logic

    return render(request, 'tables/staff/tables/table_detail.html', {
        'table': table,
        'current_order': current_order,
        'page': f'Table {table.table_number} Details',
        'current_section': 'Table Detail',
    })

from django.views.decorators.http import require_POST
@admin_required
def clear_all_tables(request):
    Table.objects.all().delete()
    messages.success(request, "All tables have been deleted.")
    return redirect('table:available_tables')

@admin_required
def clear_all_rooms(request):
    Room.objects.all().delete()  # This will also delete associated tables if models.CASCADE is set
    messages.success(request, "All rooms and their associated tables have been deleted.")
    return redirect('table:available_rooms')