from django.utils.timezone import now
from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    product_link = models.URLField(max_length=500)
    image_url = models.URLField(max_length=500)
    product_name = models.CharField(max_length=255)
    product_price = models.CharField(max_length=50)  
    rating = models.FloatField(null=True, blank=True)
    number_of_ratings = models.CharField(max_length=50)  
    specifications = models.TextField()
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.product_name


class ScrapedProduct(models.Model):
    product_link = models.URLField(max_length=500)
    image_url = models.URLField(max_length=500)
    product_name = models.CharField(max_length=255)
    product_price = models.CharField(max_length=50)
    rating = models.CharField(max_length=10, null=True, blank=True)
    number_of_ratings = models.CharField(max_length=50, null=True, blank=True)
    specifications = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product_name
    


class HistoricalData(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, default=1)
    product_name = models.CharField(max_length=255)
    price = models.FloatField()
    rating = models.FloatField(null=True, blank=True)
    date = models.DateField()

    def __str__(self):
        return f"{self.product_name} - {self.date} - {self.price}"
    



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'