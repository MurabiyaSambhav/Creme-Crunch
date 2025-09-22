# myapp/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
import os

# ----------------------------
# Custom User
# ----------------------------
class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.username
    
# ----------------------------
# Category (supports subcategories via self-reference)
# ----------------------------

    def __str__(self):
        return self.name
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    def __str__(self):
        return f"{self.product.name} - Image"
    
class Weight(models.Model):
    product = models.ForeignKey("Product",on_delete=models.CASCADE,related_name="weights")
    weight = models.CharField(max_length=50)
    def __str__(self):
        return f"{self.product.name} - {self.weight}"
    class Meta:
        db_table = "bakery_weight"


class ProductImages(models.Model):
    product = models.ForeignKey("Product",on_delete=models.CASCADE,related_name="image")
    image = models.ImageField(upload_to="products/")

    def __str__(self):
        return self.product.name

#  Delete image file from MEDIA when ProductImage row is deleted
@receiver(post_delete, sender=ProductImages)
def delete_product_image(sender, instance, **kwargs):
    if instance.image and os.path.exists(instance.image.path):
        print("Deleting image:", instance.image.path)
        instance.image.delete(save=False)

class ContactForm(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    message = models.TextField(max_length=180, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    message = models.TextField(max_length=180, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"
    
class BakeryCategory(models.Model):
    category_name = models.CharField(max_length=100, unique=True)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )

    class Meta:
        db_table = "bakery_categories"

    def __str__(self):
        return self.category_name

class BakerySubCategory(models.Model):
    category = models.ForeignKey(
        BakeryCategory, on_delete=models.CASCADE, related_name="subcategories"
    )
    subcategory_name = models.CharField(max_length=100)

    class Meta:
        db_table = "bakery_subcategories"

    def __str__(self):
        return f"{self.category.category_name} → {self.subcategory_name}"
