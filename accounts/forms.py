
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class CustomerRegistrationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']

    def save(self, commit=True):
        user = super().save(commit=False)

        # Public registration always creates a customer
        user.role = 'customer'
        user.is_staff = False
        user.is_superuser = False

        if commit:
            user.save()

        return user


class StaffCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']

    def save(self, commit=True):
        user = super().save(commit=False)

        user.role = 'staff'
        user.is_staff = True
        user.is_superuser = False

        if commit:
            user.save()

        return user
