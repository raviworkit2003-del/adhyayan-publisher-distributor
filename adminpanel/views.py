from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

# Create your views here.
def staff_required(user):
    return user.is_authenticated and user.is_staff


@login_required(login_url="login")
def dashboard(request):
    if not request.user.is_superuser:
        return redirect("home")
    return render(request,"adminpanel/dashboard.html")


@login_required(login_url="login")
def import_excel(request):
    if not request.user.is_superuser:
        return redirect("home")
    return render(request,"adminpanel/import_excel.html")


@login_required(login_url="login")
def logout_user(request):
    logout(request)
    return redirect("home")