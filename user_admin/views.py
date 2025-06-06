from django.shortcuts import render, redirect
# views.py
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .decorators import admin_required, staff_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


def admin_dashboard(request):
    return render(request, 'user_admin/admin_dashboard.html', {
        'page': 'Admin Dashboard',
        'current_section': 'Dashboard',
        'active_page': 'admin_dashboard'
    })

@login_required
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')  # replace 'login' with your login view name
    return render(request, 'user_admin/confirm_logout.html')

# @login_required
# def get_admin_notifications(request):
#     notifications = StaffNotification.objects.filter(
#         is_deleted=False
#     ).order_by('-created_at')[:10]  # or whatever limit you want
    
#     unread_count = StaffNotification.objects.filter(
#         is_read=False,
#         is_deleted=False
#     ).count()
    
#     notifications_data = [{
#         'id': n.id,
#         'message': n.message,
#         'type': n.type,  # Changed from notification_type to type
#         'order_id': n.order_id,
#         'payment_id': n.payment_id,
#         'created_at': n.created_at.isoformat(),
#         'is_read': n.is_read
#     } for n in notifications]
    
#     return JsonResponse({
#         'notifications': notifications_data,
#         'unread_count': unread_count
#     })

# @csrf_exempt
# @login_required
# def mark_admin_notifications_read(request):
#     if request.method == "POST":
#         StaffNotification.objects.filter(is_read=False).update(is_read=True)
#         return JsonResponse({"status": "success"})
#     return JsonResponse({"error": "Invalid request"}, status=400)