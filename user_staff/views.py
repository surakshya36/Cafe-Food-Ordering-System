from django.shortcuts import render

# Create your views here.
def staff_dashboard(request):
    return render(request, 'staff_dashboard.html', context={'page': 'Staff Dashboard'})