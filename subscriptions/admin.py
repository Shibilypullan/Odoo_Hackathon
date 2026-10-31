
from django.contrib import admin
from .models import Subscription, SubscriptionLine


class SubscriptionLineInline(admin.TabularInline):
    model = SubscriptionLine
    extra = 1


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):

    list_display = (
        'subscription_number',
        'customer',
        'plan',
        'status',
        'start_date',
        'expiry_date',
    )

    list_filter = ('status', 'created_at')

    search_fields = (
        'subscription_number',
        'customer__email',
    )

    inlines = [SubscriptionLineInline]


@admin.register(SubscriptionLine)
class SubscriptionLineAdmin(admin.ModelAdmin):

    list_display = (
        'subscription',
        'product',
        'quantity',
        'unit_price',
    )
