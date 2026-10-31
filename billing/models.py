
import uuid
from decimal import Decimal

from django.db import models
from django.conf import settings
from django.utils import timezone


def generate_invoice_number():
    return f"INV-{uuid.uuid4().hex[:10].upper()}"


class Invoice(models.Model):

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]

    invoice_number = models.CharField(
        max_length=30,
        unique=True,
        default=generate_invoice_number,
        editable=False
    )

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='invoices'
    )

    subscription = models.ForeignKey(
        'subscriptions.Subscription',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='invoices'
    )

    issue_date = models.DateField(default=timezone.localdate)

    due_date = models.DateField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_subtotal(self):
        return sum(
            (line.subtotal for line in self.lines.all()),
            Decimal("0.00")
        )

    def calculate_tax(self):
        return sum(
            (line.tax_amount for line in self.lines.all()),
            Decimal("0.00")
        )

    def calculate_total(self):
        return self.calculate_subtotal() + self.calculate_tax()

    def __str__(self):
        return self.invoice_number


class InvoiceLine(models.Model):

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='lines'
    )

    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT
    )

    variant = models.ForeignKey(
        'products.ProductVariant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    description = models.CharField(max_length=255, blank=True)

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
    def tax_amount(self):
        return self.subtotal * self.tax_rate / Decimal("100")

    @property
    def total_amount(self):
        return self.subtotal + self.tax_amount

    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.product.name}"
