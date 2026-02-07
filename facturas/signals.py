from decimal import Decimal
from django.db import transaction
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

from .models import Invoice, InvoiceLineItem, InvoicePayment
from inventario.models import StockItem
from kardex.models import KardexEntry


def _recalc_invoice(invoice_id: int):
    try:
        inv = Invoice.objects.get(pk=invoice_id)
    except Invoice.DoesNotExist:
        return
    inv.recalculate_totals()
    inv.save(update_fields=['subtotal', 'total_discount', 'total_tax', 'total'])


@receiver(post_save, sender=InvoiceLineItem)
def recalc_invoice_on_item_save(sender, instance: InvoiceLineItem, created, **kwargs):
    _recalc_invoice(instance.invoice_id)


@receiver(post_delete, sender=InvoiceLineItem)
def recalc_invoice_on_item_delete(sender, instance: InvoiceLineItem, **kwargs):
    _recalc_invoice(instance.invoice_id)


@receiver(post_save, sender=InvoicePayment)
def recalc_invoice_on_payment_save(sender, instance: InvoicePayment, created, **kwargs):
    # Placeholder: si agregamos campos de pagos en Invoice, recalcular aquí
    pass


@receiver(post_delete, sender=InvoicePayment)
def recalc_invoice_on_payment_delete(sender, instance: InvoicePayment, **kwargs):
    # Placeholder idem
    pass


@receiver(pre_save, sender=Invoice)
def post_invoice_to_kardex_when_status_changes(sender, instance: Invoice, **kwargs):
    if not instance.pk:
        return
    try:
        prev = Invoice.objects.get(pk=instance.pk)
    except Invoice.DoesNotExist:
        return
    # Transición a 'Emitida'
    if prev.status != 'posted' and instance.status == 'posted':
        with transaction.atomic():
            for line in instance.line_items.select_related('presentation').all():
                # Solo procesamos salidas por presentaciones
                if not line.presentation_id:
                    continue
                qty = line.quantity
                # Actualizar stock
                stock, _ = StockItem.objects.select_for_update().get_or_create(
                    warehouse=instance.warehouse,
                    presentation=line.presentation,
                    defaults={'quantity': Decimal('0.000'), 'reserved_quantity': Decimal('0.000')},
                )
                stock.quantity = stock.quantity - qty
                stock.save(update_fields=['quantity'])

                # Registrar kardex (salida)
                unit_cost = (line.presentation.cost or Decimal('0.00'))
                KardexEntry.objects.create(
                    warehouse=instance.warehouse,
                    presentation=line.presentation,
                    movement_type='out',
                    reference=str(instance.number),
                    reference_type='invoice',
                    qty_out=qty,
                    balance_qty=stock.quantity,
                    unit_cost=unit_cost,
                    movement_cost=(unit_cost * qty),
                    average_cost=unit_cost,
                )

