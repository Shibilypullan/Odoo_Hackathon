
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required

from .models import Product
from .forms import ProductForm


# 1. Display all products
@staff_member_required
def product_list(request):
    products = Product.objects.all().order_by('-created_at')

    return render(request, 'products/product_list.html', {
        'products': products
    })


# 2. Display one product
@staff_member_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)

    return render(request, 'products/product_detail.html', {
        'product': product
    })


# 3. Create a new product
@staff_member_required
def product_create(request):

    if request.method == 'POST':
        form = ProductForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('products:product_list')

    else:
        form = ProductForm()

    return render(request, 'products/product_form.html', {
        'form': form,
        'title': 'Add Product'
    })


# 4. Update an existing product
@staff_member_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)

        if form.is_valid():
            form.save()
            return redirect('products:product_list')

    else:
        form = ProductForm(instance=product)

    return render(request, 'products/product_form.html', {
        'form': form,
        'title': 'Edit Product'
    })


# 5. Delete a product
@staff_member_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        product.delete()
        return redirect('products:product_list')

    return render(request, 'products/product_confirm_delete.html', {
        'product': product
    })
