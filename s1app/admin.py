from django.contrib import admin
from .models import Author
from .models import Category
from .models import Publisher
from .models import Book
from .models import CustomerProfile
from .models import Cart
from .models import CartItem
from .models import Order
from .models import OrderItem
from .models import PublicationRequest
# Register your models here.
admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Publisher)
admin.site.register(Book)
admin.site.register(CustomerProfile)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(PublicationRequest)