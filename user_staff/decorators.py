from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required

# Decorator for admin-only views
def admin_required(view_func):
    @wraps(view_func)
    @login_required(login_url='/login/')
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied("Only admin can access this page.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# Decorator for staff-only views (admin can also access)
def staff_required(view_func):
    @wraps(view_func)
    @login_required(login_url='/login/')
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied("Only staff members can access this page.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# Optional: for only staff but NOT admin
def only_staff_required(view_func):
    @wraps(view_func)
    @login_required(login_url='/login/')
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser or not request.user.is_staff:
            raise PermissionDenied("Only non-admin staff members can access this page.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view
