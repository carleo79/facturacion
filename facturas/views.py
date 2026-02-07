from django.urls import reverse_lazy
from django.views.generic import ListView, DeleteView, DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.shortcuts import render, redirect
from django.db import transaction
from .models import Invoice, InvoiceLineItem, InvoicePayment
from .forms import InvoiceForm, InvoiceLineItemFormSet


class InvoiceListView(ListView):
    model = Invoice
    paginate_by = 20


class InvoiceCreateView(CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'facturas/invoice_form.html'
    success_url = reverse_lazy('facturas:list')

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        formset = InvoiceLineItemFormSet()
        return render(request, self.template_name, { 'form': form, 'formset': formset })

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        formset = InvoiceLineItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            invoice = form.save()
            formset.instance = invoice
            items = formset.save(commit=False)
            for it in items:
                # Autocompletar desde presentación si falta
                if it.presentation_id:
                    if not it.sku:
                        it.sku = it.presentation.sku or it.product.sku
                    if not it.name:
                        it.name = it.product.name
                    if not it.unit_of_measure:
                        it.unit_of_measure = it.presentation.unit_of_measure
                    if not it.unit_price or it.unit_price == 0:
                        it.unit_price = it.presentation.base_price
                it.invoice = invoice
                it.save()
            formset.save_m2m()
            return redirect(self.success_url)
        return render(request, self.template_name, { 'form': form, 'formset': formset })


class InvoiceUpdateView(UpdateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'facturas/invoice_form.html'
    success_url = reverse_lazy('facturas:list')

    def get(self, request, *args, **kwargs):
        invoice = self.get_object()
        form = self.form_class(instance=invoice)
        formset = InvoiceLineItemFormSet(instance=invoice)
        return render(request, self.template_name, { 'form': form, 'formset': formset, 'object': invoice })

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        invoice = self.get_object()
        form = self.form_class(request.POST, instance=invoice)
        formset = InvoiceLineItemFormSet(request.POST, instance=invoice)
        if form.is_valid() and formset.is_valid():
            invoice = form.save()
            items = formset.save(commit=False)
            # Marcar eliminados
            for obj in formset.deleted_objects:
                obj.delete()
            for it in items:
                if it.presentation_id:
                    if not it.sku:
                        it.sku = it.presentation.sku or it.product.sku
                    if not it.name:
                        it.name = it.product.name
                    if not it.unit_of_measure:
                        it.unit_of_measure = it.presentation.unit_of_measure
                    if not it.unit_price or it.unit_price == 0:
                        it.unit_price = it.presentation.base_price
                it.invoice = invoice
                it.save()
            formset.save_m2m()
            return redirect(self.success_url)
        return render(request, self.template_name, { 'form': form, 'formset': formset, 'object': invoice })


class InvoiceDeleteView(DeleteView):
    model = Invoice
    success_url = reverse_lazy('facturas:list')


# ========== Líneas de Factura (anidadas por factura) ==========
class InvoiceLineItemListView(ListView):
    model = InvoiceLineItem
    template_name = 'facturas/item_list.html'

    def get_queryset(self):
        return InvoiceLineItem.objects.filter(invoice_id=self.kwargs['invoice_id']).order_by('-created_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['invoice'] = Invoice.objects.get(pk=self.kwargs['invoice_id'])
        return ctx


class InvoiceLineItemCreateView(CreateView):
    model = InvoiceLineItem
    template_name = 'facturas/item_form.html'
    fields = [
        'product', 'presentation', 'sku', 'name', 'presentation_name', 'description',
        'quantity', 'unit_of_measure', 'unit_price',
        'discount_type', 'discount_value', 'discount_reason',
        'batch_number', 'serial_number', 'expiration_date',
    ]

    def form_valid(self, form):
        form.instance.invoice_id = self.kwargs['invoice_id']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('facturas:items:list', kwargs={'invoice_id': self.kwargs['invoice_id']})


class InvoiceLineItemUpdateView(UpdateView):
    model = InvoiceLineItem
    template_name = 'facturas/item_form.html'
    fields = [
        'product', 'presentation', 'sku', 'name', 'presentation_name', 'description',
        'quantity', 'unit_of_measure', 'unit_price',
        'discount_type', 'discount_value', 'discount_reason',
        'batch_number', 'serial_number', 'expiration_date',
    ]

    def get_success_url(self):
        return reverse_lazy('facturas:items:list', kwargs={'invoice_id': self.object.invoice_id})


class InvoiceLineItemDeleteView(DeleteView):
    model = InvoiceLineItem
    template_name = 'facturas/item_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('facturas:items:list', kwargs={'invoice_id': self.object.invoice_id})


# ========== Pagos de Factura (anidados por factura) ==========
class InvoicePaymentListView(ListView):
    model = InvoicePayment
    template_name = 'facturas/payment_list.html'

    def get_queryset(self):
        return InvoicePayment.objects.filter(invoice_id=self.kwargs['invoice_id']).order_by('-received_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['invoice'] = Invoice.objects.get(pk=self.kwargs['invoice_id'])
        return ctx


class InvoicePaymentCreateView(CreateView):
    model = InvoicePayment
    template_name = 'facturas/payment_form.html'
    fields = ['method', 'amount', 'reference']

    def form_valid(self, form):
        form.instance.invoice_id = self.kwargs['invoice_id']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('facturas:payments:list', kwargs={'invoice_id': self.kwargs['invoice_id']})


class InvoicePaymentUpdateView(UpdateView):
    model = InvoicePayment
    template_name = 'facturas/payment_form.html'
    fields = ['method', 'amount', 'reference']

    def get_success_url(self):
        return reverse_lazy('facturas:payments:list', kwargs={'invoice_id': self.object.invoice_id})


class InvoicePaymentDeleteView(DeleteView):
    model = InvoicePayment
    template_name = 'facturas/payment_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('facturas:payments:list', kwargs={'invoice_id': self.object.invoice_id})


class InvoicePrintView(DetailView):
    model = Invoice
    template_name = 'facturas/invoice_print.html'

    def get_queryset(self):
        return (
            super().get_queryset()
            .select_related('customer', 'warehouse')
            .prefetch_related('line_items__presentation', 'line_items__product', 'payments')
        )
