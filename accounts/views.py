from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomerRegistrationForm


def register(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                "Your account has been created successfully. Please log in."
            )
            return redirect('login')

    else:
        form = CustomerRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})