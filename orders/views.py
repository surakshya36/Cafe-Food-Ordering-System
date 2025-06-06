
from django.shortcuts import render, get_object_or_404, redirect
from .models import Order
from .decorators import admin_required, staff_required,login_required
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Case, When, Value, IntegerField
from .models import Order
from django.db.models.functions import Coalesce,Concat
from django.db.models import Case, When, Value, IntegerField, F, BooleanField, Q
from user_staff.models import Notification

@admin_required
def admin_all_orders_view(request):
    orders = Order.objects.annotate(
        # First: completion_status will be 0 for unpaid, 1 for paid
        completion_status=Case(
            When(status='PAID', then=Value(1)),
            default=Value(0),
            output_field=IntegerField()
        ),
        # Then: priority grouping (0=VIP+Rush, 1=VIP, 2=Rush, 3=Normal)
        priority=Case(
            When(Q(order_type='vip') & Q(is_rush=True), then=Value(0)),
            When(Q(order_type='vip') & ~Q(is_rush=True), then=Value(1)),
            When(Q(order_type='normal') & Q(is_rush=True), then=Value(2)),
            default=Value(3),
            output_field=IntegerField()
        ),
        table_number_display=Coalesce(F('table__table_number'), Value('N/A')),
        room_display=Coalesce(
            Concat(
                F('table__room__name'),
                Value(' ('),
                F('table__room__room_type'),
                Value(')')
            ),
            Value('N/A')
        ),
        total_amount_display=F('total_amount'),
        is_vip=Case(
            When(order_type='vip', then=Value(True)),
            default=Value(False),
            output_field=BooleanField()
        )
    ).order_by('completion_status', 'priority', 'created_at')  # Add completion_status first

    return render(request, 'orders/admin/all_orders.html', {
        'orders': orders,
        'active_tab': 'all',
        'page': 'All Orders'
    })


@admin_required
@login_required
def adnin_vip_orders_view(request):
    orders = Order.objects.filter(order_type='vip').annotate(  # Changed to use order_type field
        priority=Case(
            When(is_rush=True, then=Value(0)),  # VIP + Rush
            default=Value(1),                   # VIP only
            output_field=IntegerField()
        ),
        table_number_display=Coalesce(F('table__table_number'), Value('N/A')),
        total_amount_display=F('total_amount')  # Changed from total_price to total_amount
    ).order_by('priority', 'created_at')

    return render(request, 'orders/admin/all_orders.html', {
        'orders': orders,
        'active_tab': 'vip',
        'page': 'All VIP Orders'

    })
@admin_required
@login_required
def adnin_rush_orders_view(request):
    orders = Order.objects.filter(
        is_rush=True,
        order_type='normal'  # Changed to use order_type field
    ).annotate(
        table_number_display=Coalesce(F('table__table_number'), Value('N/A')),
        total_amount_display=F('total_amount'),  # Changed from total_price to total_amount
        is_vip=Value(False, output_field=BooleanField())
    ).order_by('created_at')

    return render(request, 'orders/admin/all_orders.html', {
        'orders': orders,
        'active_tab': 'rush',
        'page': 'All Rush Orders'

    })
@admin_required
@login_required
def adnin_normal_orders_view(request):
    orders = Order.objects.filter(
        is_rush=False,
        order_type='normal'  # Changed to use order_type field
    ).annotate(
        table_number_display=Coalesce(F('table__table_number'), Value('N/A')),
        total_amount_display=F('total_amount'),  # Changed from total_price to total_amount
        is_vip=Value(False, output_field=BooleanField())
    ).order_by('created_at')

    return render(request, 'orders/admin/all_orders.html', {
        'orders': orders,
        'active_tab': 'normal',
        'page': 'All Normal Orders'

    })

@admin_required
@login_required
def admin_all_orders_ajax(request):
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        tab = request.GET.get('tab', 'all')

        orders = Order.objects.all()

        # Filter based on the tab
        if tab == 'vip':
            orders = orders.filter(order_type='vip')
        elif tab == 'rush':
            # Filter for rush orders that are NOT VIP
            orders = orders.filter(is_rush=True).exclude(order_type='vip')
        elif tab == 'normal':
            orders = orders.filter(order_type='normal', is_rush=False)

        # Annotate and sort
        orders = orders.annotate(
            completion_status=Case(
                When(status='PAID', then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            ),
            priority=Case(
                When(Q(order_type='vip') & Q(is_rush=True), then=Value(0)),  # Highest priority
                When(Q(order_type='vip') & ~Q(is_rush=True), then=Value(1)),
                When(Q(order_type='normal') & Q(is_rush=True), then=Value(2)),
                default=Value(3),  # Lowest priority
                output_field=IntegerField()
            ),
            table_number_display=Coalesce(F('table__table_number'), Value('N/A')),
            room_display=Coalesce(
                Concat(
                    F('table__room__name'),
                    Value(' ('), F('table__room__room_type'), Value(')')
                ),
                Value('N/A')
            ),
            total_amount_display=F('total_amount'),
            is_vip=Case(
                When(order_type='vip', then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        ).order_by('completion_status', 'priority', 'created_at')

        html = render_to_string('orders/admin/order_row.html', {'orders': orders, 'active_tab': tab})
        return JsonResponse({'html': html})

    return JsonResponse({'error': 'Invalid request'}, status=400)

@admin_required
@login_required
def adnin_order_detail_view(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        context = {'order': order, 
        'page': 'View Order Detail'
                   }
        return render(request, 'orders/admin/order_detail.html', context)
    except Order.DoesNotExist:
        # Handle case where order doesn't exist
        return redirect('some_error_page_or_orders_list')

@admin_required
@login_required
def adnin_edit_order_status(request, order_id):
    # Get the order with related data efficiently
    order = get_object_or_404(
        Order.objects.select_related('table__room'),
        id=order_id
    )
    
    # Prepare status choices from the model
    status_choices = Order._meta.get_field('status').choices
    
    if request.method == 'POST':
        return admin_update_order_status(request, order)
    
    context = {
        'order': order,
        'status_choices': status_choices,
        'table_number': order.table.table_number if order.table else 'N/A',
        'room_info': f"{order.table.room.name} ({order.table.room.get_room_type_display()})" 
                     if (order.table and order.table.room) else 'N/A',
        'grand_total': order.total_amount,
        'page': 'Edit Order Status'
    }
    return render(request, 'orders/admin/edit_status.html', context)
@admin_required
@login_required
def admin_update_order_status(request, order):
    new_status = request.POST.get('status')
    status_choices = dict(Order._meta.get_field('status').choices)
    
    if new_status in status_choices:
        order.status = new_status
        order.save()
        messages.success(request, f'Order #{order.id} status updated to {status_choices[new_status]}')
        return redirect('admin_order_detail_view', order_id=order.id)
    else:
        messages.error(request, 'Invalid status selected')
        return redirect('admin_edit_order_status', order_id=order.id)


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from orders.models import Order
from django.views.decorators.http import require_http_methods

@admin_required
@login_required
@require_http_methods(["GET", "POST"])
def admin_order_delete(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        # Get the table associated with this order
        associated_table = order.table
        
        # Delete the order
        order.delete()
        
        # Update the table that was associated with this order
        if associated_table:
            associated_table.status = 'AVAILABLE'
            associated_table.current_order = None
            associated_table.save()
        
        messages.success(request, f"Order #{order_id} deleted successfully.")
        return redirect('admin_all_orders_view')  # adjust to your actual orders list view name

    return render(request, 'orders/admin/confirm_delete.html', {'order': order, 'page': 'Confirm Delete Order'})


@admin_required
def clear_all_orders(request):
    # Delete all orders
    Order.objects.all().delete()
    
    # Update all tables: set status to AVAILABLE and clear current_order
    from tables.models import Table
    
    Table.objects.update(status='AVAILABLE', current_order=None)
    
    return redirect('admin_all_orders_view')


# staff views
@staff_required
def staff_all_orders_view(request):
    orders = Order.objects.annotate(
        # First: completion_status will be 0 for unpaid, 1 for paid
        completion_status=Case(
            When(status='PAID', then=Value(1)),
            default=Value(0),
            output_field=IntegerField()
        ),
        # Then: priority grouping (0=VIP+Rush, 1=VIP, 2=Rush, 3=Normal)
        priority=Case(
            When(Q(order_type='vip') & Q(is_rush=True), then=Value(0)),
            When(Q(order_type='vip') & ~Q(is_rush=True), then=Value(1)),
            When(Q(order_type='normal') & Q(is_rush=True), then=Value(2)),
            default=Value(3),
            output_field=IntegerField()
        ),
        table_number_display=Coalesce(F('table__table_number'), Value('N/A')),
        room_display=Coalesce(
            Concat(
                F('table__room__name'),
                Value(' ('),
                F('table__room__room_type'),
                Value(')')
            ),
            Value('N/A')
        ),
        total_amount_display=F('total_amount'),
        is_vip=Case(
            When(order_type='vip', then=Value(True)),
            default=Value(False),
            output_field=BooleanField()
        )
    ).order_by('completion_status', 'priority', 'created_at')  # Add completion_status first

    return render(request, 'orders/staff/all_orders.html', {
        'orders': orders,
        'active_tab': 'all'
    })



def staff_vip_orders_view(request):
    orders = Order.objects.filter(order_type='vip').annotate(  # Changed to use order_type field
        priority=Case(
            When(is_rush=True, then=Value(0)),  # VIP + Rush
            default=Value(1),                   # VIP only
            output_field=IntegerField()
        ),
        table_number_display=Coalesce(F('table__table_number'), Value('N/A')),
        total_amount_display=F('total_amount')  # Changed from total_price to total_amount
    ).order_by('priority', 'created_at')

    return render(request, 'orders/staff/all_orders.html', {
        'orders': orders,
        'active_tab': 'vip'
    })

def staff_rush_orders_view(request):
    orders = Order.objects.filter(
        is_rush=True,
        order_type='normal'  # Changed to use order_type field
    ).annotate(
        table_number_display=Coalesce(F('table__table_number'), Value('N/A')),
        total_amount_display=F('total_amount'),  # Changed from total_price to total_amount
        is_vip=Value(False, output_field=BooleanField())
    ).order_by('created_at')

    return render(request, 'orders/staff/all_orders.html', {
        'orders': orders,
        'active_tab': 'rush'
    })

def staff_normal_orders_view(request):
    orders = Order.objects.filter(
        is_rush=False,
        order_type='normal'  # Changed to use order_type field
    ).annotate(
        table_number_display=Coalesce(F('table__table_number'), Value('N/A')),
        total_amount_display=F('total_amount'),  # Changed from total_price to total_amount
        is_vip=Value(False, output_field=BooleanField())
    ).order_by('created_at')

    return render(request, 'orders/staff/all_orders.html', {
        'orders': orders,
        'active_tab': 'normal'
    })


def staff_all_orders_ajax(request):
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        tab = request.GET.get('tab', 'all')

        orders = Order.objects.all()

        # Filter based on the tab
        if tab == 'vip':
            orders = orders.filter(order_type='vip')
        elif tab == 'rush':
            # Filter for rush orders that are NOT VIP
            orders = orders.filter(is_rush=True).exclude(order_type='vip')
        elif tab == 'normal':
            orders = orders.filter(order_type='normal', is_rush=False)

        # Annotate and sort
        orders = orders.annotate(
            completion_status=Case(
                When(status='PAID', then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            ),
            priority=Case(
                When(Q(order_type='vip') & Q(is_rush=True), then=Value(0)),  # Highest priority
                When(Q(order_type='vip') & ~Q(is_rush=True), then=Value(1)),
                When(Q(order_type='normal') & Q(is_rush=True), then=Value(2)),
                default=Value(3),  # Lowest priority
                output_field=IntegerField()
            ),
            table_number_display=Coalesce(F('table__table_number'), Value('N/A')),
            room_display=Coalesce(
                Concat(
                    F('table__room__name'),
                    Value(' ('), F('table__room__room_type'), Value(')')
                ),
                Value('N/A')
            ),
            total_amount_display=F('total_amount'),
            is_vip=Case(
                When(order_type='vip', then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        ).order_by('completion_status', 'priority', 'created_at')

        html = render_to_string('orders/staff/order_row.html', {'orders': orders, 'active_tab': tab})
        return JsonResponse({'html': html})

    return JsonResponse({'error': 'Invalid request'}, status=400)



def staff_order_detail_view(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        context = {'order': order}
        return render(request, 'orders/staff/order_detail.html', context)
    except Order.DoesNotExist:
        # Handle case where order doesn't exist
        return redirect('some_error_page_or_orders_list')

# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Order

@login_required
def staff_edit_order_status(request, order_id):
    # Get the order with related data efficiently
    order = get_object_or_404(
        Order.objects.select_related('table__room'),
        id=order_id
    )
    
    # Prepare status choices from the model
    status_choices = Order._meta.get_field('status').choices
    
    if request.method == 'POST':
        return update_order_status(request, order)
    
    context = {
        'order': order,
        'status_choices': status_choices,
        'table_number': order.table.table_number if order.table else 'N/A',
        'room_info': f"{order.table.room.name} ({order.table.room.get_room_type_display()})" 
                     if (order.table and order.table.room) else 'N/A',
        'grand_total': order.total_amount,
    }
    return render(request, 'orders/staff/edit_status.html', context)

# views.py
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib import messages
from django.shortcuts import redirect

def update_order_status(request, order):
    # Get the new status from POST data
    new_status = request.POST.get('status')
    status_choices = dict(Order._meta.get_field('status').choices)

    # Validate status
    if new_status not in status_choices:
        messages.error(request, 'Invalid status selected')
        return redirect('staff_edit_order_status', order_id=order.id)

    try:
        # Update order status
        old_status = order.status
        order.status = new_status
        order.save()

        # Prepare friendly notification message
        if new_status == 'confirmed':
            notification_message = f'Your order #{order.id} has been confirmed.'
        elif new_status == 'preparing':
            notification_message = f'Your order #{order.id} is being prepared.'
        elif new_status == 'ready':
            notification_message = f'Your order #{order.id} is ready for pickup.'
        elif new_status == 'delivered':
            notification_message = f'Your order #{order.id} has been delivered.'
        elif new_status == 'cancelled':
            notification_message = f'Your order #{order.id} has been cancelled.'
        else:
            notification_message = (
                f'Your order #{order.id} status has been updated to {status_choices.get(new_status, "updated")}.'
            )

        # Create notification
        Notification.objects.create(
            type='order_Status',
            message=notification_message,
            order=order,
            session_key=order.session_key,  # Use order's original session
            metadata={
                'order_id': order.id,
                'old_status': old_status,
                'new_status': new_status,
                'status_display': status_choices.get(new_status)
            },
            is_read=False
        )

        # Add success message for staff
        messages.success(
            request,
            f'Order #{order.id} status updated from '
            f'{status_choices.get(old_status, "N/A")} to {status_choices.get(new_status)}'
        )

        return redirect('staff_order_detail_view', order_id=order.id)

    except Exception as e:
        # Log the error (you might want to use proper logging here)
        print(f"Error updating order status: {str(e)}")
        
        # Revert order status if save failed
        if hasattr(order, 'old_status'):
            order.status = old_status
        
        messages.error(
            request,
            f'Failed to update order status. Error: {str(e)}'
        )
        return redirect('staff_edit_order_status', order_id=order.id)
