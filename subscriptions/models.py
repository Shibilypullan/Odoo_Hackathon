
from django.db import models
from django.conf import settings
from products.models import Product, ProductVariant, Plan
import uuid


def generate_subscription_number():
    return f"SUB-{uuid.uuid4().hex[:10].upper()}"


class Subscription(models.Model):

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('quotation', 'Quotation'),
        ('confirmed', 'Confirmed'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('closed', 'Closed'),
    ]

    subscription_number = models.CharField(
        max_length=20,
        unique=True,
        default=generate_subscription_number,
        editable=False
    )

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='subscriptions'
    )

    plan = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        related_name='subscriptions'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )

    start_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)

    quotation_valid_until = models.DateField(
        null=True,
        blank=True
    )

    payment_terms = models.CharField(
        max_length=200,
        blank=True
    )

    renewal_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subscription_number


class SubscriptionLine(models.Model):

    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='lines'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    quantity = models.PositiveIntegerField(default=1)

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    @property
    def subtotal(self):
        return self.quantity * self.unit_price

    @property
    def total_amount(self):
        return self.subtotal * (1 + self.tax_rate / 100)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
