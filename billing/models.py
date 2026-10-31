
import uuid
from decimal import Decimal

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


def generate_invoice_number():
    return f"INV-{uuid.uuid4().hex[:8].upper()}"


class Invoice(models.Model):

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('partially_paid', 'Partially Paid'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]

    invoice_number = models.CharField(
        max_length=30,
        unique=True,
        default=generate_invoice_number
    )

    customer = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='invoices'
    )

    subscription = models.ForeignKey(
        'subscriptions.Subscription',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices'
    )

    issue_date = models.DateField(default=timezone.localdate)
    due_date = models.DateField()

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
            Decimal('0.00')
        )

    def calculate_tax(self):
        return sum(
            (line.tax_amount for line in self.lines.all()),
            Decimal('0.00')
        )

    def calculate_total(self):
        return self.calculate_subtotal() + self.calculate_tax()

    @property
    def paid_amount(self):
        return sum(
            (payment.amount for payment in self.payments.all()),
            Decimal('0.00')
        )

    @property
    def balance_due(self):
        return max(
            self.calculate_total() - self.paid_amount,
            Decimal('0.00')
        )

    @property
    def is_overdue(self):
        return (
            self.due_date < timezone.localdate()
            and self.balance_due > 0
            and self.status != 'cancelled'
            and self.status != 'draft'
        )

    def update_payment_status(self):
        if self.status in ['draft', 'cancelled']:
            return

        total = self.calculate_total()
        paid = self.paid_amount

        if total > 0 and paid >= total:
            new_status = 'paid'
        elif paid > 0:
            new_status = 'partially_paid'
        else:
            new_status = 'confirmed'

        if self.status != new_status:
            self.status = new_status
            self.save(update_fields=['status'])

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
        default=Decimal('0.00')
    )

    @property
    def subtotal(self):
        return self.quantity * self.unit_price

    @property
    def tax_amount(self):
        return self.subtotal * self.tax_rate / Decimal('100')

    @property
    def total_amount(self):
        return self.subtotal + self.tax_amount

    def __str__(self):
        return f"{self.product} - {self.quantity}"


class Payment(models.Model):

    PAYMENT_METHODS = [
        ('upi', 'UPI'),
        ('card', 'Card'),
        ('bank', 'Bank Transfer'),
        ('cash', 'Cash'),
    ]

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.PROTECT,
        related_name='payments'
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS
    )

    payment_date = models.DateField(default=timezone.localdate)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()

        if self.amount is None or self.amount <= 0:
            raise ValidationError({
                'amount': 'Payment amount must be greater than zero.'
            })

        if self.invoice_id:
            previous_payments = self.invoice.payments.exclude(pk=self.pk)

            already_paid = sum(
                (payment.amount for payment in previous_payments),
                Decimal('0.00')
            )

            invoice_total = self.invoice.calculate_total()

            if already_paid + self.amount > invoice_total:
                raise ValidationError({
                    'amount': (
                        f'Payment exceeds the remaining balance of '
                        f'{invoice_total - already_paid}.'
                    )
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        self.invoice.update_payment_status()

    def delete(self, *args, **kwargs):
        invoice = self.invoice
        result = super().delete(*args, **kwargs)
        invoice.update_payment_status()
        return result

    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.amount}"
