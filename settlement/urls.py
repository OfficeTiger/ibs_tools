
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('invoices/', views.InvoiceListView.as_view(), name='invoices'),
    path('invoice/<int:pk>', views.InvoiceDetailView.as_view(), name='invoice-detail'),
    path('invoice/create/', views.InvoiceCreate.as_view(), name='invoice_create')
]
