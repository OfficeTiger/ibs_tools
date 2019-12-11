from django.db import models
from datetime import datetime
from datetime import timedelta
from docx.shared import Cm
from docxtpl import DocxTemplate, InlineImage
from django.conf import settings
from .models import Invoice
import pandas as pd


def format_number(x):
    return(format(x, ",.2f").replace(".", ";").replace(",", ".").replace(";", ","))

class InvoiceGenerator_donotuse():
    invoice = None

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


class WorkingHoursGenerator():
    def __init__(self, xls_file):
        self.excel_doc = xls_file

    def generate(template, month):
        xls = pd.ExcelFile(xls_file)
        working_time = xls.parse(month)
