from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.conf import settings
import os


# ----------------------------
# Custom User
# ----------------------------
class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username


# ----------------------------
# Category (Merged with Subcategory)
# ----------------------------
class BakeryCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children"
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bakery_categories"
        verbose_name_plural = "Bakery Categories"

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} → {self.name}"
        return self.name


# ----------------------------
# Product
# ----------------------------
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Top-level category
    category = models.ForeignKey(
        'BakeryCategory',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="products"
    )

    # Subcategories (ManyToMany for child categories)
    subcategories = models.ManyToManyField(
        'BakeryCategory',
        blank=True,
        related_name='products_subcategories'
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
# ----------------------------
# Product Weights / Prices
# ----------------------------
class Weight(models.Model):
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="weights")
    weight = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bakery_weight"

    def __str__(self):
        return f"{self.product.name} - {self.weight} (₹{self.price})"

# ----------------------------
# Product Images
# ----------------------------
class ProductImages(models.Model):
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/")
    is_main = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - {'Main' if self.is_main else 'Sub'}"


@receiver(post_delete, sender=ProductImages)
def delete_product_image(sender, instance, **kwargs):
    if instance.image and os.path.exists(instance.image.path):
        print("Deleting image:", instance.image.path)
        instance.image.delete(save=False)


# ----------------------------
# Contact Form
# ----------------------------
class ContactForm(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    message = models.TextField(max_length=180, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.email}"

# ----------------------------
# Cart
# ----------------------------

class BakeryCart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart_items"
    )
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="cart_entries"
    )
    category = models.ForeignKey(
        "BakeryCategory",  # Correct model name
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cart_entries"
    )
    weight = models.ForeignKey(
        "Weight",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cart_entries"
    )
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        """Calculate total price for this cart item."""
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"