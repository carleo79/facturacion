from django import forms
from django.forms import inlineformset_factory
from .models import Invoice, InvoiceLineItem


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['number', 'customer', 'warehouse', 'currency', 'status', 'notes']


class InvoiceLineItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceLineItem
        fields = [
            'product', 'presentation', 'sku', 'name', 'presentation_name', 'description',
            'quantity', 'unit_of_measure', 'unit_price',
            'discount_type', 'discount_value', 'discount_reason',
            'batch_number', 'serial_number', 'expiration_date',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Relajar requeridos para no bloquear la emisión si falta autocompletar
        self.fields['sku'].required = False
        self.fields['name'].required = False


InvoiceLineItemFormSet = inlineformset_factory(
    parent_model=Invoice,
    model=InvoiceLineItem,
    form=InvoiceLineItemForm,
    extra=0,
    can_delete=True,
)
