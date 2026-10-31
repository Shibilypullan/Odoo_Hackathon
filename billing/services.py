from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Invoice, InvoiceLine


@transaction.atomic
def generate_invoice_from_subscription(subscription):

    # Only confirmed or active subscriptions can be invoiced
    if subscription.status not in ['confirmed', 'active']:
        raise ValidationError(
            "Invoice can only be generated for confirmed or active subscriptions."
        )

    issue_date = timezone.localdate()

    # Prevent duplicate invoices for the same subscription on the same date
    if Invoice.objects.filter(
        subscription=subscription,
        issue_date=issue_date
    ).exists():
        raise ValidationError(
            "An invoice already exists for this subscription today."
        )

    subscription_lines = subscription.lines.select_related(
        'product', 'variant'
    ).all()

    if not subscription_lines.exists():
        raise ValidationError(
            "Cannot generate an invoice because the subscription has no items."
        )

    # Create the invoice
    invoice = Invoice.objects.create(
        customer=subscription.customer,
        subscription=subscription,
        issue_date=issue_date,
        status='draft'
    )

    # Copy subscription items into invoice lines
    for line in subscription_lines:
        InvoiceLine.objects.create(
            invoice=invoice,
            product=line.product,
            variant=line.variant,
            description=line.product.name,
            quantity=line.quantity,
            unit_price=line.unit_price,
            tax_rate=line.tax_rate
        )

    return invoice