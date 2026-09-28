from django.urls import path
from . import views

app_name = "adminpanel"

urlpatterns = [

    path("", views.dashboard, name="dashboard"),
    path("logout/", views.logout_user, name="logout"),
    path("import-excel/",views.import_excel,name="import_excel"),
]


