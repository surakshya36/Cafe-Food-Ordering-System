from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required(login_url='/login/')
def staff_dashboard(request):
    return render(request, 'user_staff/staff_dashboard.html', context={'page': 'Staff Dashboard'})
