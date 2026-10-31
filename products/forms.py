
from django import forms
from .models import Product


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product

        fields = [
            'name',
            'product_type',
            'sales_price',
            'cost_price',
            'notes',
        ]

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter product name'
            }),

            'product_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter product type'
            }),

            'sales_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),

            'cost_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),

            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Additional information'
            }),
        }

    def clean_name(self):
        name = self.cleaned_data['name'].strip()

        if not name:
            raise forms.ValidationError(
                'Product name cannot be empty.'
            )

        return name

    def clean_sales_price(self):
        price = self.cleaned_data['sales_price']

        if price < 0:
            raise forms.ValidationError(
                'Sales price cannot be negative.'
            )

        return price

    def clean_cost_price(self):
        price = self.cleaned_data['cost_price']

        if price < 0:
            raise forms.ValidationError(
                'Cost price cannot be negative.'
            )

        return price
