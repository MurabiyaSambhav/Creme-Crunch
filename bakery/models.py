from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.username

from django.db.models.signals import post_delete
from django.dispatch import receiver
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    description = models.TextField()
    image = models.ImageField(upload_to='product_images/')  

    
    def __str__(self):
        return self.name

class Weight(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='weights')
    weight_value = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.weight_value} for {self.product.name}"
@receiver(post_delete, sender=Product)
def delete_product_image(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)