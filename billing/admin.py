
from django.contrib import admin
from .models import Invoice, InvoiceLine, Payment


class InvoiceLineInline(admin.TabularInline):
    model = InvoiceLine
    extra = 1


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):

    list_display = (
        'invoice_number',
        'customer',
        'issue_date',
        'due_date',
        'status',
        'display_total',
        'paid_amount',
        'balance_due',
        'is_overdue',
    )

    list_filter = ('status', 'issue_date', 'due_date')

    search_fields = (
        'invoice_number',
        'customer__email',
    )

    readonly_fields = ('invoice_number', 'created_at')

    inlines = [InvoiceLineInline, PaymentInline]

    @admin.display(description='Invoice Total')
    def display_total(self, obj):
        return obj.calculate_total()

    @admin.display(description='Amount Paid')
    def paid_amount(self, obj):
        return obj.paid_amount

    @admin.display(description='Balance Due')
    def balance_due(self, obj):
        return obj.balance_due

    @admin.display(boolean=True, description='Overdue')
    def is_overdue(self, obj):
        return obj.is_overdue


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        'invoice',
        'amount',
        'payment_method',
        'payment_date',
    )

    list_filter = ('payment_method', 'payment_date')

    search_fields = ('invoice__invoice_number',)


