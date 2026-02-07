from django.db import models
from decimal import Decimal


class Supplier(models.Model):
    code = models.CharField('Código', max_length=20, unique=True)
    name = models.CharField('Nombre / Razón Social', max_length=200)
    tax_id = models.CharField('RUC/NIT', max_length=20, unique=True)
    address = models.CharField('Dirección', max_length=255, blank=True)
    phone = models.CharField('Teléfono', max_length=20, blank=True)
    email = models.EmailField('Email', blank=True)
    is_active = models.BooleanField('Activo', default=True)
    created_at = models.DateTimeField('Creado', auto_now_add=True)
    updated_at = models.DateTimeField('Actualizado', auto_now=True)

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['name']

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class PurchaseOrder(models.Model):
    STATUS = [
        ('draft', 'Borrador'),
        ('approved', 'Aprobada'),
        ('received', 'Recibida'),
        ('cancelled', 'Anulada'),
    ]

    number = models.CharField('Número', max_length=30, unique=True)
    supplier = models.ForeignKey('compras.Supplier', on_delete=models.PROTECT, related_name='purchase_orders', verbose_name='Proveedor')
    warehouse = models.ForeignKey('inventario.Warehouse', on_delete=models.PROTECT, related_name='purchase_orders', verbose_name='Bodega')
    status = models.CharField('Estado', max_length=10, choices=STATUS, default='draft')
    order_date = models.DateField('Fecha de Orden')
    received_date = models.DateField('Fecha de Recepción', null=True, blank=True)

    notes = models.TextField('Notas', blank=True)
    subtotal = models.DecimalField('Subtotal', max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_tax = models.DecimalField('Impuestos', max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField('Total', max_digits=15, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField('Creado', auto_now_add=True)

    class Meta:
        verbose_name = 'Orden de Compra'
        verbose_name_plural = 'Órdenes de Compra'
        ordering = ['-order_date', '-number']

    def __str__(self) -> str:
        return self.number


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey('compras.PurchaseOrder', on_delete=models.CASCADE, related_name='items', verbose_name='Orden de Compra')
    presentation = models.ForeignKey('productos.ProductPresentation', on_delete=models.PROTECT, related_name='purchase_items', verbose_name='Presentación')

    description = models.CharField('Descripción', max_length=255, blank=True)
    quantity = models.DecimalField('Cantidad', max_digits=15, decimal_places=3)
    unit_cost = models.DecimalField('Costo Unitario', max_digits=15, decimal_places=2)
    discount = models.DecimalField('Descuento', max_digits=15, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField('Impuesto', max_digits=15, decimal_places=2, default=Decimal('0.00'))
    line_total = models.DecimalField('Total Línea', max_digits=15, decimal_places=2)

    class Meta:
        verbose_name = 'Ítem de Orden de Compra'
        verbose_name_plural = 'Ítems de Órdenes de Compra'

    def __str__(self) -> str:
        return f"{self.purchase_order.number} - {self.presentation.sku}"
