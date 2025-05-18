from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login
from django.db.models.functions import Right
from django.db.models import IntegerField
from django.db.models.functions import Cast
from user_staff.views import *
from user_admin.views import *





User = get_user_model()




def generate_next_username():
    last_user = (
        User.objects.filter(username__startswith="staff_")
        .annotate(number_part=Right("username", 3))
        .annotate(number=Cast("number_part", IntegerField()))
        .order_by("-number")
        .first()
    )

    last_number = 0
    if last_user:
        last_number = last_user.number or 0

    next_number = last_number + 1
    return f"staff_{next_number:03d}"



def register_staff(request):
    if request.method == "POST":
        data = request.POST

        full_name = data.get('full_name')
        gender = data.get('gender')
        email = data.get('email')
        phone = data.get('phone')
        password = data.get('password')

          # auto-generate username like staff_001
        username = generate_next_username()

        user= User.objects.create_user(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            gender=gender,
            phone=phone,
            role='staff'
        )
        user.save()
        # Redirect to login with a success message
        from django.contrib import messages
        messages.success(request, f"Account created. Your username is: {username}")
        return redirect("/login/") 

    return render(request, 'register.html', context={'page': 'Staff Registration Page'})


def login_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not User.objects.filter(username = username).exists():
            messages.error(request, "User doesnot esxits.")
            return redirect("/login/")
        

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            if user.role == "admin":
                return redirect("/admin-dashboard/")
            elif user.role == "staff":
                return redirect("staff_dashboard")
            else:
                messages.error(request, "Unknown role.")
                return redirect("/login/")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("/login/")

       
    return render(request, 'login.html', context={'page':'Log In'})


