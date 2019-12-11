from django.db import models
from datetime import datetime
from django.conf import settings
from django.urls import reverse
from decimal import *
from datetime import timedelta
from docx.shared import Cm
from docxtpl import DocxTemplate, InlineImage
import pandas as pd

# https://blog.formpl.us/how-to-generate-word-documents-from-templates-using-python-cb039ea2c890
# https://github.com/Vnessah/docx-gen


class Invoice(models.Model):
    CALCULATION_MODE = (
        ('PU', 'Per unit'),
        ('LS', 'Lump-sum'),
    )
    calculation_mode = models.CharField(max_length=2,
                                        choices=CALCULATION_MODE,
                                        default='PU',
                                        verbose_name='Calculation per unit or lump sum')
    number = models.IntegerField(verbose_name='Invoice number', unique=True)
    date = models.DateField(verbose_name='Invoice date', default=datetime.now, blank=False, null=False)
    due_date = models.DateField(verbose_name='Due date', blank=False, null=False)
    working_period = models.CharField(max_length=50, verbose_name='Working period')
    template = models.FileField(verbose_name='Invoice template for generation', null=True, blank=True,
                                upload_to=settings.INVOICE_TEMPLATES_FILE_PATH)
    txt = models.CharField(max_length=300, verbose_name='Invoice text', null=True, blank=True)
    hours = models.DecimalField(verbose_name='Working hours', max_digits=6, decimal_places=2)
    hourly_rate = models.DecimalField(verbose_name='Hourly rate (paid per hour)', max_digits=6, decimal_places=2)
    net = models.DecimalField(verbose_name='Net amount', max_digits=12, decimal_places=2)
    percent_tax = models.DecimalField(verbose_name='Tax in percent', max_digits=6, decimal_places=2)
    document = models.FileField(verbose_name='Stored invoice document', null=True, blank=True,
                                upload_to=settings.INVOICE_DOCUMENTS_FILE_PATH)

    class Meta:
        ordering = ['-date']

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.number = self.next_number
        
        self.calculate()
        super(Invoice, self).save(*args, **kwargs)
        igen = InvoiceGenerator(self)


    def __str__(self):
        return "Invoice %i from %s (%s)" % (self.number, self.date.strftime("%d.%m.%Y"), self.working_period)

    def get_absolute_url(self):
        """Returns the url to access a particular instance of the model."""
        return reverse('invoice-detail', args=[str(self.id)])

    def calculate(self):
        if(self.calculation_mode == 'PU'):
            self.net = commercialRound(self.hours * self.hourly_rate)

    @property
    def tax(self):
        return(commercialRound(self.net * self.percent_tax / 100))

    @property
    def gross(self):
        return(commercialRound(float(self.net) + self.tax))

    @property
    def next_number(self):
        # According to our numbering scheme
        start_of_year = 9100000 + (datetime.today().year % 100 - 3) * 100

        # Find the largest number > start_of_year
        # If one exists, the next number is the last existing number, incremented by 1
        # If it doesn't exist (since we're creating the first number of the current year), we start by number 1
        nn = start_of_year + 1
        last_invoice = Invoice.objects.filter(number__gt=start_of_year).order_by("-number")
        if (last_invoice.count() > 0):
            nn = last_invoice[0].number + 1
        return(nn)


class TimeSheet(models.Model):
    year = models.IntegerField(verbose_name='Year of service', null=False, blank=False)
    month = models.CharField(max_length=30, verbose_name='Month of service', null=False, blank=False)
    date_of_creation = models.DateField(verbose_name='Created at', null=True, blank=True)
    total_hours = models.DecimalField(verbose_name='Total hours', null=True, blank=True, max_digits=6, decimal_places=2)
    excel_document = models.FileField(verbose_name='Excel document with daily working hours', null=False, blank=False)
    template = models.FileField(verbose_name='Word template for generation', null=False, blank=False,
                                upload_to=settings.INVOICE_TEMPLATES_FILE_PATH)
    document = models.FileField(verbose_name='Generated document', null=True, blank=True,
                                upload_to=settings.INVOICE_DOCUMENTS_FILE_PATH)



# Services starts here
def commercialRound(x):
    x = float(x)
    return(x / abs(x) * int(abs(x) * 100 + .5) / 100)

def format_number(x):
    return(format(x, ",.2f").replace(".", ";").replace(",", ".").replace(";", ","))

class InvoiceGenerator():

    def __str__(self):
        if(self.invoice is None):
            return("Invoice generator. No invoice specified.")
        else:
            return("Generator for %s" % (self.invoice))

    def __init__(self, _invoice):
        # invoice = Invoice.objects.get(invoice_id)

        # Test
        self.invoice = _invoice

    def __donotuse(self, invoice_id):
        # invoice = Invoice.objects.get(invoice_id)

        # Test
        self.invoice = Invoice()
        self.invoice.number = 9101616   # self.invoice.next_number
        self.invoice.date = datetime.now()
        self.invoice.due_date = self.invoice.date + timedelta(days=30)
        self.invoice.working_period = "September 2019"
        self.invoice.template = "./template_kindler.docx"
        self.invoice.calculation_mode = 'PU'
        self.invoice.hours = 10.5
        self.invoice.hourly_rate = 85.0
        self.invoice.percent_tax = 19.0
        self.invoice.template = r"C:\Dev\python\Django\ibs\ibs_tools\ibs_site\settlement\template_kindler.docx"
        self.invoice.calculate()

    @property
    def content(self):
        return {
            'invoice_no': self.invoice.number,
            'date': self.invoice.date.strftime("%d.%m.%Y"),
            'working_period': self.invoice.working_period,
            'txt': self.invoice.txt,
            'hours': format_number(self.invoice.hours),
            'hourly_rate': format_number(self.invoice.hourly_rate),
            'net': format_number(self.invoice.net),
            'percent_tax': format_number(self.invoice.percent_tax),
            'tax': format_number(self.invoice.tax),
            'gross': format_number(self.invoice.gross),
            'due_date': self.invoice.due_date.strftime("%d.%m.%Y"),
        }

    @property
    def document_name(self):
        recipient = "kindler"
        return("%i-%s-%s" % (self.invoice.number, self.invoice.date.strftime("%Y%m%d"), recipient))

    def generate(self):
        template = DocxTemplate(self.invoice.template)
        template.render(self.content)
        docx_name = r"C:\Dev\python\Django\ibs\ibs_tools\ibs_site\settlement\%s.docx" % (self.document_name)
        self.invoice.document = docx_name
        self.invoice.save()
        template.save(docx_name)


class TimesheetGenerator():
    def __init__(self, xls_file):
        self.excel_doc = xls_file

    def generate(template, month):
        xls = pd.ExcelFile(xls_file)
        working_time = xls.parse(month)
