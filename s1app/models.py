from django.db import models
from django.contrib.auth.models import User


PAYMENT_STATUS = [
    ("Pending", "Pending"),
    ("Paid", "Paid"),
    ("Failed", "Failed"),
    ("Refunded", "Refunded"),
]

ORDER_STATUS = [
    ("Pending", "Pending"),
    ("Confirmed", "Confirmed"),
    ("Packed", "Packed"),
    ("Shipped", "Shipped"),
    ("Delivered", "Delivered"),
    ("Cancelled", "Cancelled"),
]



######################################  Master Data  ######################
class Author(models.Model):
    name=models.CharField(max_length=100)
    phone = models.CharField(max_length=15)

    email = models.EmailField()
    biography = models.TextField(blank=True)

    country = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name


class Publisher(models.Model):
    Phone = models.CharField(max_length=15)
    Email = models.EmailField()

    company_name = models.CharField(max_length=100)
    address = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to="publisher_logo/",blank=True)



    
    def __str__(self):
        return self.company_name



###############################   BOOK   ########################################


class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.ManyToManyField(Author)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)

    publisher = models.ForeignKey(Publisher,on_delete=models.CASCADE)
    isbn = models.CharField(max_length=20,unique=True)

    language = models.CharField(max_length=50)
    number_of_pages = models.IntegerField()

    edition = models.CharField(max_length=50)
    price = models.DecimalField( max_digits=8,decimal_places=2)

    description = models.TextField()
    publish_date = models.DateField()

    available = models.BooleanField(default=True)
    stock_quantity = models.PositiveIntegerField(default=0) 

    featured_book = models.BooleanField(default=False)

    created_at= models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    cover_image = models.ImageField(upload_to="book_covers/", blank=True)
    thumbnail = models.URLField(blank=True)
    pdf_preview = models.FileField(upload_to="book_preview/", blank=True)




    def __str__(self):
        return self.title




 ##########################  Customer    ################################3

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    address = models.TextField()

    country = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)

    postal_code = models.CharField(max_length=10)
    profile_image = models.ImageField(upload_to="profile_images/", blank=True)


    def __str__(self):
        return self.user.username

##############################    Shopping Cart       ########################


class Cart(models.Model):
    customer = models.OneToOneField(CustomerProfile,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.customer.user.username


class CartItem(models.Model):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE)
    book = models.ForeignKey(Book,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.book.title}({self.quantity})"



######################## Orders #######################


class Order(models.Model):
    customer = models.ForeignKey(CustomerProfile,on_delete=models.CASCADE)
    order_number = models.CharField(max_length=30, unique=True)

    total_price = models.DecimalField(max_digits=8,decimal_places=2)

    payment_status = models.CharField(max_length=20,choices=PAYMENT_STATUS,default="Pending")
    order_status = models.CharField(max_length=20,choices=ORDER_STATUS,default="Pending")

    shipping_address = models.TextField()

    order_date = models.DateField()
    delivered_date = models.DateField(null = True,blank=True)

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    book = models.ForeignKey(Book,on_delete=models.CASCADE)

    quantity = models.PositiveBigIntegerField(default=1)
    price = models.DecimalField(max_digits=8,decimal_places=2)


    def __str__(self):
        return f"{self.book.title} ({self.quantity})"


class PublicationRequest(models.Model):
    author_name = models.CharField(max_length=100)
    email = models.EmailField()

    phone = models.CharField(max_length=15)

    manuscript_title = models.TextField()

    manuscript_file = models.FileField(upload_to="book_preview/", blank=True)

    description = models.TextField(blank= True)

    status = models.CharField(max_length=20,choices=PAYMENT_STATUS,default="Pending")

    submitted_at = models.DateTimeField(auto_now_add=True)
