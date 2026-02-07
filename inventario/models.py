from django.db import models
from decimal import Decimal


class Warehouse(models.Model):
    name = models.CharField('Nombre', max_length=100, unique=True)
    code = models.CharField('Código', max_length=20, unique=True)
    address = models.CharField('Dirección', max_length=255, blank=True)
    is_active = models.BooleanField('Activo', default=True)
    created_at = models.DateTimeField('Creado', auto_now_add=True)
    updated_at = models.DateTimeField('Actualizado', auto_now=True)

    class Meta:
        verbose_name = 'Bodega'
        verbose_name_plural = 'Bodegas'
        ordering = ['name']

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class StockItem(models.Model):
    """
    Stock por presentación y bodega.
    Nota: ProductPresentation vive en productos.models
    """
    warehouse = models.ForeignKey('inventario.Warehouse', on_delete=models.CASCADE, related_name='stock_items', verbose_name='Bodega')
    presentation = models.ForeignKey('productos.ProductPresentation', on_delete=models.CASCADE, related_name='stock_items', verbose_name='Presentación')

    quantity = models.DecimalField('Cantidad', max_digits=15, decimal_places=3, default=Decimal('0.000'))
    reserved_quantity = models.DecimalField('Reservado', max_digits=15, decimal_places=3, default=Decimal('0.000'))

    min_quantity = models.DecimalField('Mínimo', max_digits=15, decimal_places=3, default=Decimal('0.000'))
    max_quantity = models.DecimalField('Máximo', max_digits=15, decimal_places=3, null=True, blank=True)
    reorder_point = models.DecimalField('Punto de Reorden', max_digits=15, decimal_places=3, null=True, blank=True)

    location = models.CharField('Ubicación', max_length=100, blank=True)
    is_active = models.BooleanField('Activo', default=True)
    updated_at = models.DateTimeField('Actualizado', auto_now=True)

    class Meta:
        verbose_name = 'Item de Stock'
        verbose_name_plural = 'Items de Stock'
        unique_together = [['warehouse', 'presentation']]
        indexes = [
            models.Index(fields=['warehouse', 'presentation']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self) -> str:
        return f"{self.warehouse.code} - {self.presentation.sku}"

    @property
    def available_quantity(self):
        return self.quantity - self.reserved_quantity


class InventoryAdjustment(models.Model):
    """Ajustes de inventario manuales por bodega/presentación"""
    ADJUSTMENT_TYPE = [
        ('increase', 'Aumento'),
        ('decrease', 'Disminución'),
    ]

    warehouse = models.ForeignKey('inventario.Warehouse', on_delete=models.PROTECT, related_name='adjustments', verbose_name='Bodega')
    presentation = models.ForeignKey('productos.ProductPresentation', on_delete=models.PROTECT, related_name='adjustments', verbose_name='Presentación')
    adjustment_type = models.CharField('Tipo', max_length=10, choices=ADJUSTMENT_TYPE)
    quantity = models.DecimalField('Cantidad', max_digits=15, decimal_places=3)
    reason = models.CharField('Motivo', max_length=255, blank=True)
    reference = models.CharField('Referencia', max_length=50, blank=True)
    created_at = models.DateTimeField('Creado', auto_now_add=True)

    class Meta:
        verbose_name = 'Ajuste de Inventario'
        verbose_name_plural = 'Ajustes de Inventario'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.adjustment_type} {self.quantity} {self.presentation.sku} @ {self.warehouse.code}"
