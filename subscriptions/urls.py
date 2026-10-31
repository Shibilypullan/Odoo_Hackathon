from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    # Quotation pages
    path(
        'quotations/',
        views.quotation_list,
        name='quotation_list'
    ),

    path(
        'quotations/create/',
        views.quotation_create,
        name='quotation_create'
    ),

    # Quotation details
    path(
        'quotations/<int:pk>/',
        views.quotation_detail,
        name='quotation_detail'
    ),

    # Subscription lifecycle actions
    path(
        '<int:pk>/action/<str:action>/',
        views.subscription_action,
        name='subscription_action'
    ),
]