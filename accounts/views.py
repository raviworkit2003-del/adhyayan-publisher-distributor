from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login as auth_login
from django.contrib.auth.models import User

# Create your views here.
def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user =  authenticate(
            request,
            username=username,
            password=password
            )

        if user is not None:
                auth_login(request, user)
                if user.is_superuser:
                    return redirect("adminpanel:dashboard")
                return redirect("home")
        else:
            return render(
                request,
                "accounts/login.html",
                {"error": "Invalid username or password."}
            )

    return render(request,"accounts/login.html")

def register(request):
    if request.method == "POST":
        username=request.POST.get("username")
        email=request.POST.get("email")
        password=request.POST.get("password")
        password2=request.POST.get("password2")

        if password != password2:
            return render(request,"accounts/register.html",{"error": "Passwords do not match."})

        if User.objects.filter(username=username).exists():
            return render(request, "accounts/register.html", {"error": "Username already exists."})



        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        return redirect("login")

    return render(request,"accounts/register.html")