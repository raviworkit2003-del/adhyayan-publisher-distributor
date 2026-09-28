from django.urls import path
from . import views

urlpatterns = [
    path("",views.home,name="home"),
    path("books/",views.books,name="books"),
    path("books/<int:id>/", views.book_detail,name="book_detail"),
    path("publish_with_us/",views.publish_with_us, name="publish_with_us"),
    path("category/",views.category,name="category"), 
]

