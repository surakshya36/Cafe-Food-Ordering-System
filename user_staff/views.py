from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .decorators import admin_required, staff_required
from user_staff.models import Notification

@staff_required
def staff_dashboard(request):
    return render(request, 'user_staff/staff_dashboard.html', {
        'page': 'Staff Dashboard',
        'current_section': 'Dashboard',
        'active_page': 'staff_dashboard'
    })

@login_required
@staff_required
def staff_logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')  # replace 'login' with your login view name
    return render(request, 'user_staff/confirm_logout.html')

# views.py
from django.http import JsonResponse
from .models import Notification
from django.urls import reverse
@login_required
def get_staff_notifications(request):
    # Filter only order and payment notifications
    notifications = Notification.objects.filter(
        type__in=['order', 'payment'],
        is_deleted=False
    ).order_by('-created_at')

    data = []
    for n in notifications:
        url = None
        if n.type == 'order' and n.metadata.get('order_id'):
            url = reverse('staff_edit_order_status', kwargs={'order_id': n.metadata.get('order_id')})
        elif n.type == 'payment' and n.metadata.get('payment_id'):
            url = reverse('staff_order_detail_view', kwargs={'payment_id': n.metadata.get('payment_id')})

        data.append({
            'id': n.id,
            'message': n.message,
            'created_at': n.created_at.strftime("%Y-%m-%d %H:%M"),
            'is_read': n.is_read,
            'type': n.type,
            'order_id': n.metadata.get('order_id') if n.type == 'order' else None,
            'payment_id': n.metadata.get('payment_id') if n.type == 'payment' else None,
            'url': url,
        })

    unread_count = Notification.objects.filter(
        is_read=False,
        is_deleted=False,
        type__in=['order', 'payment']
    ).count()

    return JsonResponse({'notifications': data, 'unread_count': unread_count})



@require_POST
@login_required
def soft_clear_all_staff_notifications(request):
    """
    Soft delete all staff notifications by marking them as deleted
    """
    try:
        # If your model has a 'is_deleted' field, use this approach
        updated_count = Notification.objects.filter(is_deleted=False).update(is_deleted=True)
        
        return JsonResponse({
            'success': True, 
            'message': f'Successfully cleared {updated_count} notifications',
            'cleared_count': updated_count
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e),
            'message': 'Failed to clear notifications'
        }, status=500)

# views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt
@login_required

def mark_staff_notifications_read(request):
    if request.method == "POST":
        Notification.objects.filter(is_read=False).update(is_read=True)
        return JsonResponse({"status": "success"})
    return JsonResponse({"error": "Invalid request"}, status=400)





