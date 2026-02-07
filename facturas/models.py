from django.db import models
from decimal import Decimal


class InvoiceStatus(models.TextChoices):
    DRAFT = 'draft', 'Borrador'
    POSTED = 'posted', 'Emitida'
    CANCELLED = 'cancelled', 'Anulada'


class PaymentMethod(models.TextChoices):
    CASH = 'cash', 'Efectivo'
    CARD = 'card', 'Tarjeta'
    TRANSFER = 'transfer', 'Transferencia'
    CREDIT = 'credit', 'Crédito'


class Invoice(models.Model):
    """Cabecera de factura de venta"""
    number = models.CharField('Número', max_length=30, unique=True)
    date = models.DateTimeField('Fecha', auto_now_add=True)

    customer = models.ForeignKey(
        'clientes.Cliente',
        on_delete=models.PROTECT,
        related_name='invoices',
        verbose_name='Cliente'
    )

    warehouse = models.ForeignKey(
        'inventario.Warehouse',
        on_delete=models.PROTECT,
        related_name='invoices',
        verbose_name='Bodega'
    )

    currency = models.CharField('Moneda', max_length=3, default='COP')
    status = models.CharField('Estado', max_length=20, choices=InvoiceStatus.choices, default=InvoiceStatus.DRAFT)

    subtotal = models.DecimalField('Subtotal', max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_discount = models.DecimalField('Total Descuento', max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_tax = models.DecimalField('Total Impuestos', max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField('Total', max_digits=15, decimal_places=2, default=Decimal('0.00'))

    notes = models.TextField('Notas', blank=True)
    created_at = models.DateTimeField('Creado', auto_now_add=True)
    updated_at = models.DateTimeField('Actualizado', auto_now=True)

    class Meta:
        verbose_name = 'Factura'
        verbose_name_plural = 'Facturas'
        ordering = ['-date']

    def __str__(self) -> str:
        return f"FAC-{self.number}"

    def recalculate_totals(self):
        """Recalcula totales a partir de las líneas."""
        agg_subtotal = Decimal('0.00')
        agg_discount = Decimal('0.00')
        agg_tax = Decimal('0.00')
        for line in self.line_items.all():
            line.calculate_totals()
            agg_subtotal += line.subtotal
            agg_discount += line.discount_amount
            agg_tax += line.total_tax
        self.subtotal = agg_subtotal
        self.total_discount = agg_discount
        self.total_tax = agg_tax
        self.total = self.subtotal + self.total_tax
        return self.total

    def clean(self):
        from django.core.exceptions import ValidationError
        # Validar stock suficiente al emitir
        if self.status == InvoiceStatus.POSTED:
            # Cargar líneas existentes (en edición). Si es creación con formset, esta validación se aplicará al actualizar a Emitida
            insufficient = []
            # Importación perezosa para evitar ciclos
            from inventario.models import StockItem
            for line in self.line_items.select_related('presentation', 'product').all():
                # Requiere presentación para descontar inventario de forma precisa
                if not line.presentation_id:
                    insufficient.append(f"Línea {line.sku or line.name}: falta seleccionar Presentación")
                    continue
                try:
                    stock = StockItem.objects.get(warehouse=self.warehouse, presentation=line.presentation)
                    available = stock.quantity - stock.reserved_quantity
                    if line.quantity > available:
                        insufficient.append(
                            f"{line.presentation.sku}: stock insuficiente en {self.warehouse.code}. Disponible {available}, requerido {line.quantity}"
                        )
                except StockItem.DoesNotExist:
                    insufficient.append(f"{line.presentation.sku}: no existe stock en bodega {self.warehouse.code}")
            if insufficient:
                raise ValidationError({
                    'status': ['No se puede Emitir por falta de stock:'] + insufficient
                })


class InvoicePayment(models.Model):
    """Pagos aplicados a una factura"""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments', verbose_name='Factura')
    method = models.CharField('Método', max_length=20, choices=PaymentMethod.choices)
    amount = models.DecimalField('Monto', max_digits=15, decimal_places=2)
    reference = models.CharField('Referencia', max_length=50, blank=True)
    received_at = models.DateTimeField('Fecha de Pago', auto_now_add=True)

    class Meta:
        verbose_name = 'Pago de Factura'
        verbose_name_plural = 'Pagos de Facturas'

    def __str__(self) -> str:
        return f"{self.invoice.number} - {self.method}: {self.amount}"


# Importaciones al final para evitar ciclos entre apps
from productos.models import (  # noqa: E402
    UnitOfMeasure,
    DiscountType,
    Product,
    ProductPresentation,
)


class InvoiceLineItem(models.Model):
    """Línea de factura/ítem de producto o presentación"""
    invoice = models.ForeignKey('facturas.Invoice', on_delete=models.CASCADE, related_name='line_items', verbose_name='Factura')

    # Referencia a producto base
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='invoice_items',
        verbose_name='Producto'
    )

    # Referencia a presentación específica (opcional)
    presentation = models.ForeignKey(
        ProductPresentation,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='invoice_items',
        verbose_name='Presentación'
    )

    # Información al momento de la venta
    sku = models.CharField('SKU', max_length=50, help_text='SKU de la presentación o producto')
    name = models.CharField('Nombre', max_length=255)
    presentation_name = models.CharField('Nombre de Presentación', max_length=255, blank=True)
    description = models.TextField('Descripción', blank=True)

    # Cantidades
    quantity = models.DecimalField(
        'Cantidad',
        max_digits=15,
        decimal_places=3,
        validators=[]
    )
    unit_of_measure = models.CharField('Unidad', max_length=20, choices=UnitOfMeasure.choices)

    # Precios
    unit_price = models.DecimalField(
        'Precio Unitario',
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )

    # Descuento
    discount_type = models.CharField(
        'Tipo de Descuento',
        max_length=20,
        choices=DiscountType.choices,
        blank=True,
        null=True
    )
    discount_value = models.DecimalField(
        'Valor de Descuento',
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    discount_amount = models.DecimalField(
        'Monto de Descuento',
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    discount_reason = models.CharField('Razón del Descuento', max_length=255, blank=True)

    # Totales
    subtotal = models.DecimalField(
        'Subtotal',
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Antes de impuestos'
    )
    total_tax = models.DecimalField('Total Impuestos', max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField('Total', max_digits=15, decimal_places=2, default=Decimal('0.00'))

    # Control de inventario (opcional)
    batch_number = models.CharField('Número de Lote', max_length=50, blank=True)
    serial_number = models.CharField('Número de Serie', max_length=50, blank=True)
    expiration_date = models.DateField('Fecha de Vencimiento', null=True, blank=True)

    created_at = models.DateTimeField('Creado', auto_now_add=True)

    class Meta:
        verbose_name = 'Línea de Factura'
        verbose_name_plural = 'Líneas de Factura'

    def __str__(self):
        return f"{self.sku} - {self.name} x {self.quantity}"

    def calculate_totals(self):
        """Calcula subtotal, descuentos, impuestos y total"""
        subtotal_before_discount = self.unit_price * self.quantity

        # Calcular descuento
        if self.discount_type == DiscountType.PERCENTAGE:
            self.discount_amount = (subtotal_before_discount * self.discount_value) / 100
        elif self.discount_type == DiscountType.FIXED:
            self.discount_amount = self.discount_value
        else:
            self.discount_amount = Decimal('0.00')

        # Subtotal después de descuento
        self.subtotal = subtotal_before_discount - self.discount_amount

        # Calcular impuestos
        self.total_tax = Decimal('0.00')
        for tax in self.line_taxes.all():
            self.total_tax += tax.amount

        # Total
        self.total = self.subtotal + self.total_tax
        return self.total


class LineItemTax(models.Model):
    """Impuestos aplicados a una línea de factura"""
    line_item = models.ForeignKey(
        InvoiceLineItem,
        on_delete=models.CASCADE,
        related_name='line_taxes',
        verbose_name='Línea de Factura'
    )
    tax_type = models.CharField('Tipo de Impuesto', max_length=20)
    name = models.CharField('Nombre', max_length=100)
    rate = models.DecimalField('Tasa (%)', max_digits=5, decimal_places=2)
    base = models.DecimalField('Base Gravable', max_digits=15, decimal_places=2)
    amount = models.DecimalField('Monto', max_digits=15, decimal_places=2)

    class Meta:
        verbose_name = 'Impuesto de Línea'
        verbose_name_plural = 'Impuestos de Líneas'

    def __str__(self):
        return f"{self.line_item.sku} - {self.name}: ${self.amount}"
