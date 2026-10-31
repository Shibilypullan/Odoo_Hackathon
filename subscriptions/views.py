
import calendar
from datetime import date, timedelta

from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from products.models import Plan
from .models import Subscription, SubscriptionLine


User = get_user_model()


# --------------------------------------------------
# QUOTATION FORM
# --------------------------------------------------

class QuotationForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = [
            'customer',
            'plan',
            'quotation_valid_until',
            'payment_terms',
            'start_date',
            'expiry_date',
        ]

        widgets = {
            'quotation_valid_until': forms.DateInput(
                attrs={'type': 'date'}
            ),
            'start_date': forms.DateInput(
                attrs={'type': 'date'}
            ),
            'expiry_date': forms.DateInput(
                attrs={'type': 'date'}
            ),
            'payment_terms': forms.TextInput(
                attrs={
                    'placeholder': 'Example: Payment due within 15 days'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['customer'].queryset = User.objects.filter(
            role='customer'
        )

        self.fields['plan'].queryset = Plan.objects.filter(
            is_active=True
        )

    def clean(self):
        cleaned_data = super().clean()

        start_date = cleaned_data.get('start_date')
        expiry_date = cleaned_data.get('expiry_date')
        quotation_valid_until = cleaned_data.get(
            'quotation_valid_until'
        )

        if start_date and expiry_date and expiry_date < start_date:
            self.add_error(
                'expiry_date',
                'Expiry date cannot be before the start date.'
            )

        if (
            quotation_valid_until
            and quotation_valid_until < date.today()
        ):
            self.add_error(
                'quotation_valid_until',
                'Quotation validity date cannot be in the past.'
            )

        return cleaned_data


# --------------------------------------------------
# PERMISSION CHECK
# --------------------------------------------------

def staff_required(user):
    """Allow staff and admin users to manage subscriptions."""

    return (
        user.is_authenticated
        and (
            user.is_superuser
            or user.is_staff
            or getattr(user, 'role', None) in ['admin', 'staff']
        )
    )


# --------------------------------------------------
# BILLING PERIOD CALCULATION
# --------------------------------------------------

def add_billing_period(start_date, frequency):
    """
    Calculate the next date based on the plan billing frequency.
    Handles months and years with different numbers of days.
    """

    if frequency == 'daily':
        return start_date + timedelta(days=1)

    if frequency == 'weekly':
        return start_date + timedelta(weeks=1)

    if frequency == 'monthly':
        year = start_date.year
        month = start_date.month + 1

        if month > 12:
            month = 1
            year += 1

        last_day = calendar.monthrange(year, month)[1]
        day = min(start_date.day, last_day)

        return date(year, month, day)

    if frequency == 'yearly':
        year = start_date.year + 1
        last_day = calendar.monthrange(year, start_date.month)[1]
        day = min(start_date.day, last_day)

        return date(year, start_date.month, day)

    raise ValueError('Unsupported billing frequency.')


# --------------------------------------------------
# QUOTATION LIST
# --------------------------------------------------

@login_required
def quotation_list(request):
    if not staff_required(request.user):
        raise PermissionDenied

    quotations = (
        Subscription.objects
        .filter(status='quotation')
        .select_related('customer', 'plan')
        .order_by('-created_at')
    )

    return render(
        request,
        'subscriptions/quotation_list.html',
        {'quotations': quotations}
    )


# --------------------------------------------------
# CREATE QUOTATION
# --------------------------------------------------

@login_required
def quotation_create(request):
    if not staff_required(request.user):
        raise PermissionDenied

    if request.method == 'POST':
        form = QuotationForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                quotation = form.save(commit=False)
                quotation.status = 'quotation'
                quotation.save()

                SubscriptionLine.objects.create(
                    subscription=quotation,
                    product=quotation.plan.product,
                    quantity=quotation.plan.minimum_quantity,
                    unit_price=quotation.plan.price,
                    tax_rate=0,
                )

            messages.success(
                request,
                'Quotation created successfully.'
            )

            return redirect(
                'subscriptions:quotation_detail',
                pk=quotation.pk
            )

    else:
        form = QuotationForm()

    return render(
        request,
        'subscriptions/quotation_form.html',
        {'form': form}
    )


# --------------------------------------------------
# QUOTATION / SUBSCRIPTION DETAILS
# --------------------------------------------------

@login_required
def quotation_detail(request, pk):
    subscription = get_object_or_404(
        Subscription.objects.select_related(
            'customer',
            'plan',
            'plan__product'
        ),
        pk=pk
    )

    if (
        not staff_required(request.user)
        and subscription.customer_id != request.user.pk
    ):
        raise PermissionDenied

    lines = subscription.lines.select_related(
        'product',
        'variant'
    ).all()

    total_amount = sum(
        (line.total_amount for line in lines),
        start=0
    )

    return render(
        request,
        'subscriptions/quotation_detail.html',
        {
            'quotation': subscription,
            'subscription': subscription,
            'lines': lines,
            'total_amount': total_amount,
        }
    )


# --------------------------------------------------
# SUBSCRIPTION LIFECYCLE ACTIONS
# --------------------------------------------------

@login_required
@require_POST
def subscription_action(request, pk, action):

    if not staff_required(request.user):
        raise PermissionDenied

    today = timezone.localdate()

    with transaction.atomic():
        subscription = get_object_or_404(
            Subscription.objects.select_for_update().select_related(
                'plan'
            ),
            pk=pk
        )

        plan = subscription.plan

        # CONFIRM QUOTATION
        if action == 'confirm':

            if subscription.status != 'quotation':
                messages.error(
                    request,
                    'Only quotations can be confirmed.'
                )

            elif (
                subscription.quotation_valid_until
                and subscription.quotation_valid_until < today
            ):
                messages.error(
                    request,
                    'This quotation has expired.'
                )

            else:
                subscription.status = 'confirmed'
                subscription.save(update_fields=['status'])

                messages.success(
                    request,
                    'Quotation confirmed successfully.'
                )

        # ACTIVATE SUBSCRIPTION
        elif action == 'activate':

            if subscription.status != 'confirmed':
                messages.error(
                    request,
                    'Only confirmed subscriptions can be activated.'
                )

            elif not subscription.start_date or not subscription.expiry_date:
                messages.error(
                    request,
                    'Please set the start date and expiry date first.'
                )

            elif subscription.expiry_date < subscription.start_date:
                messages.error(
                    request,
                    'Expiry date cannot be before the start date.'
                )

            elif subscription.start_date > today:
                messages.error(
                    request,
                    'This subscription cannot be activated before its start date.'
                )

            elif subscription.expiry_date < today:
                messages.error(
                    request,
                    'This subscription has already expired.'
                )

            else:
                subscription.status = 'active'
                subscription.save(update_fields=['status'])

                messages.success(
                    request,
                    'Subscription activated successfully.'
                )

        # PAUSE SUBSCRIPTION
        elif action == 'pause':

            if subscription.status != 'active':
                messages.error(
                    request,
                    'Only active subscriptions can be paused.'
                )

            elif not plan.allow_pause:
                messages.error(
                    request,
                    'Pausing is not allowed for this plan.'
                )

            else:
                subscription.status = 'paused'
                subscription.save(update_fields=['status'])

                messages.success(
                    request,
                    'Subscription paused successfully.'
                )

        # RESUME SUBSCRIPTION
        elif action == 'resume':

            if subscription.status != 'paused':
                messages.error(
                    request,
                    'Only paused subscriptions can be resumed.'
                )

            elif (
                subscription.expiry_date
                and subscription.expiry_date < today
            ):
                messages.error(
                    request,
                    'This subscription has expired and cannot be resumed.'
                )

            else:
                subscription.status = 'active'
                subscription.save(update_fields=['status'])

                messages.success(
                    request,
                    'Subscription resumed successfully.'
                )

        # RENEW SUBSCRIPTION
        elif action == 'renew':

            if subscription.status != 'active':
                messages.error(
                    request,
                    'Only active subscriptions can be renewed.'
                )

            elif not plan.allow_renewal:
                messages.error(
                    request,
                    'Renewal is not allowed for this plan.'
                )

            elif not subscription.expiry_date:
                messages.error(
                    request,
                    'An expiry date is required before renewal.'
                )

            else:
                next_start = subscription.expiry_date + timedelta(days=1)

                next_expiry = add_billing_period(
                    next_start,
                    plan.billing_frequency
                )

                # Keep the original start date unchanged.
                subscription.expiry_date = next_expiry
                subscription.renewal_count += 1

                subscription.save(
                    update_fields=[
                        'expiry_date',
                        'renewal_count'
                    ]
                )

                messages.success(
                    request,
                    'Subscription renewed successfully.'
                )

        # CLOSE SUBSCRIPTION
        elif action == 'close':

            if subscription.status not in ['active', 'paused']:
                messages.error(
                    request,
                    'Only active or paused subscriptions can be closed.'
                )

            elif not plan.allow_early_close:
                messages.error(
                    request,
                    'Early closure is not allowed for this plan.'
                )

            else:
                subscription.status = 'closed'
                subscription.save(update_fields=['status'])

                messages.success(
                    request,
                    'Subscription closed successfully.'
                )

        else:
            messages.error(
                request,
                'Invalid subscription action.'
            )

    return redirect(
        'subscriptions:quotation_detail',
        pk=pk
    )
