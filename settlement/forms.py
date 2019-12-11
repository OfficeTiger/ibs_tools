from django import forms

class InvoiceForm(forms.Form):
    invoice_date = forms.DateField(help_text="Enter the invoice date.")