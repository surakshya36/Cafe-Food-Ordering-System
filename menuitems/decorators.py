from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def staff_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return view_func(request, *args, **kwargs)
        messages.error(request, "You must be a staff member to access this page.")
        return redirect('login')  # or any other page you want to redirect to
    return _wrapped_view

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        messages.error(request, "You must be an admin to access this page.")
        return redirect('login')
    return _wrapped_view
