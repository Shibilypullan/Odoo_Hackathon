
from django.db import models


class Product(models.Model):

    name = models.CharField(max_length=200)

    product_type = models.CharField(max_length=100)

    sales_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ProductVariant(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants'
    )

    brand = models.CharField(max_length=100)

    additional_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    def __str__(self):
        return f"{self.product.name} - {self.brand}"


class Plan(models.Model):

    BILLING_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    name = models.CharField(max_length=200)

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='plans'
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    billing_frequency = models.CharField(
        max_length=20,
        choices=BILLING_CHOICES
    )

    minimum_quantity = models.PositiveIntegerField(default=1)

    available_from = models.DateField()
    available_until = models.DateField(null=True, blank=True)

    auto_close = models.BooleanField(default=False)
    allow_early_close = models.BooleanField(default=True)
    allow_pause = models.BooleanField(default=True)
    allow_renewal = models.BooleanField(default=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
