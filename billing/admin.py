
from django.contrib import admin
from .models import Invoice, InvoiceLine


class InvoiceLineInline(admin.TabularInline):
    model = InvoiceLine
    extra = 1


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):

    list_display = (
        'invoice_number',
        'customer',
        'subscription',
        'issue_date',
        'due_date',
        'status',
    )

    list_filter = ('status', 'issue_date')

    search_fields = (
        'invoice_number',
        'customer__username',
    )

    inlines = [InvoiceLineInline]


@admin.register(InvoiceLine)
class InvoiceLineAdmin(admin.ModelAdmin):

    list_display = (
        'invoice',
        'product',
        'quantity',
        'unit_price',
        'tax_rate',
    )
