
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from products.models import Plan
from .models import Subscription, SubscriptionLine


User = get_user_model()


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
            'quotation_valid_until': forms.DateInput(attrs={'type': 'date'}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'payment_terms': forms.TextInput(
                attrs={'placeholder': 'Example: Payment due within 15 days'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Only customer accounts can be selected for a quotation.
        self.fields['customer'].queryset = User.objects.filter(role='customer')

        # Only active plans can be selected.
        self.fields['plan'].queryset = Plan.objects.filter(is_active=True)


def staff_required(user):
    """Allow subscription management to staff and admin accounts."""
    return (
        user.is_authenticated
        and (
            user.is_superuser
            or user.is_staff
            or user.role in ['admin', 'staff']
        )
    )


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

                # Create the initial product line from the selected plan.
                SubscriptionLine.objects.create(
                    subscription=quotation,
                    product=quotation.plan.product,
                    quantity=quotation.plan.minimum_quantity,
                    unit_price=quotation.plan.price,
                    tax_rate=0,
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


@login_required
def quotation_detail(request, pk):
    quotation = get_object_or_404(
        Subscription.objects.select_related('customer', 'plan'),
        pk=pk,
        status='quotation'
    )

    # Staff/admin can view any quotation; customers can only view their own.
    if not staff_required(request.user) and quotation.customer_id != request.user.pk:
        raise PermissionDenied

    lines = quotation.lines.select_related('product', 'variant').all()

    total_amount = sum(
        (line.total_amount for line in lines),
        start=0
    )

    return render(
        request,
        'subscriptions/quotation_detail.html',
        {
            'quotation': quotation,
            'lines': lines,
            'total_amount': total_amount,
        }
    )