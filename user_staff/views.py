from django.shortcuts import render, redirect
# views.py
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required


def staff_dashboard(request):
    return render(request, 'user_staff/staff_dashboard.html', {
        'page': 'Staff Dashboard',
        'current_section': 'Dashboard',
        'active_page': 'staff_dashboard'
    })

@login_required
def staff_logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')  # replace 'login' with your login view name
    return render(request, 'user_staff/confirm_logout.html')
