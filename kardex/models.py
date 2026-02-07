from django.db import models
from decimal import Decimal


class KardexEntry(models.Model):
    """
    Movimiento de inventario por presentación y bodega, con costo promedio móvil.
    """
    MOVEMENT_TYPE = [
        ('in', 'Entrada'),
        ('out', 'Salida'),
        ('adjust', 'Ajuste'),
    ]

    date = models.DateTimeField('Fecha', auto_now_add=True)
    warehouse = models.ForeignKey('inventario.Warehouse', on_delete=models.PROTECT, related_name='kardex_entries', verbose_name='Bodega')
    presentation = models.ForeignKey('productos.ProductPresentation', on_delete=models.PROTECT, related_name='kardex_entries', verbose_name='Presentación')
    movement_type = models.CharField('Tipo', max_length=10, choices=MOVEMENT_TYPE)

    # Referencia externa (orden de compra, factura, ajuste)
    reference = models.CharField('Referencia', max_length=50, blank=True)
    reference_type = models.CharField('Tipo de Referencia', max_length=30, blank=True)

    # Cantidades
    qty_in = models.DecimalField('Cantidad Entrada', max_digits=15, decimal_places=3, default=Decimal('0.000'))
    qty_out = models.DecimalField('Cantidad Salida', max_digits=15, decimal_places=3, default=Decimal('0.000'))
    balance_qty = models.DecimalField('Saldo Cantidad', max_digits=15, decimal_places=3, default=Decimal('0.000'))

    # Costos
    unit_cost = models.DecimalField('Costo Unitario', max_digits=15, decimal_places=6, default=Decimal('0.000000'))
    movement_cost = models.DecimalField('Costo del Movimiento', max_digits=15, decimal_places=2, default=Decimal('0.00'))
    average_cost = models.DecimalField('Costo Promedio', max_digits=15, decimal_places=6, default=Decimal('0.000000'))

    class Meta:
        verbose_name = 'Entrada de Kardex'
        verbose_name_plural = 'Entradas de Kardex'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['presentation', 'warehouse', 'date']),
        ]

    def __str__(self) -> str:
        return f"{self.date:%Y-%m-%d %H:%M} {self.presentation.sku} {self.movement_type}"
