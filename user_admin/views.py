from django.shortcuts import render, redirect
# views.py
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required


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
