from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from settlement.models import Invoice, TimeSheet
#from settlement.forms import InvoiceForm
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy

def index(request):
    """View function for home page"""

    num_invoices = Invoice.objects.count()
    num_time_sheets = TimeSheet.objects.count()

    context = {
        'num_invoices': num_invoices,
        'num_time_sheets': num_time_sheets,
    }

    return(render(request, 'index.html', context=context))


class InvoiceListView(generic.ListView):
    model = Invoice


class InvoiceDetailView(generic.DetailView):
    model = Invoice


class InvoiceCreate(CreateView):
    model = Invoice
    fields = ['calculation_mode', 'date', 'due_date', 'working_period', 'hours', 'hourly_rate', 'percent_tax', 'template']

