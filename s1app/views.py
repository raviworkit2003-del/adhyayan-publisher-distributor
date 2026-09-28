from django.shortcuts import render
from .models import Book
from django.core.paginator import Paginator
def home(request):
    featured_books = Book.objects.all()[:4]

    return render(
        request,
        "home/home.html",
        {
            "featured_book": featured_books,
        }
    )
def books(request):
    books=Book.objects.select_related(
        "category",
        "publisher"
    ).all()
    paginator = Paginator(books,12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
    }

    return render(request,"book/book_list.html", context)

def book_detail(request, id):
    book=Book.objects.get(id=id)
    context = {
        "book":book,

    }

    return render(request,"book/book_detail.html",context)

def publish_with_us(request):
    return render(request,"publication/publish_with_us.html")
def category(request):
    return render(request,"category/category.html")