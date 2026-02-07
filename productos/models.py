"""
models.py - Estructura de Productos para Sistema de Facturación Django
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()


# ============================================
# CHOICES (Enums)
# ============================================

class ProductType(models.TextChoices):
    PRODUCT = 'product', 'Producto Físico'
    SERVICE = 'service', 'Servicio'
    DIGITAL = 'digital', 'Producto Digital'
    SUBSCRIPTION = 'subscription', 'Suscripción'


class TaxType(models.TextChoices):
    IVA = 'iva', 'IVA'
    EXEMPT = 'exempt', 'Exento'
    EXCLUDED = 'excluded', 'Excluido'


class ProductStatus(models.TextChoices):
    ACTIVE = 'active', 'Activo'
    INACTIVE = 'inactive', 'Inactivo'
    DISCONTINUED = 'discontinued', 'Descontinuado'


class UnitOfMeasure(models.TextChoices):
    UNIT = 'unit', 'Unidad'
    KG = 'kg', 'Kilogramo'
    G = 'g', 'Gramo'
    L = 'l', 'Litro'
    ML = 'ml', 'Mililitro'
    M = 'm', 'Metro'
    CM = 'cm', 'Centímetro'
    M2 = 'm2', 'Metro Cuadrado'
    M3 = 'm3', 'Metro Cúbico'
    HOUR = 'hour', 'Hora'
    DAY = 'day', 'Día'
    MONTH = 'month', 'Mes'
    PACKAGE = 'package', 'Paquete'


class DiscountType(models.TextChoices):
    PERCENTAGE = 'percentage', 'Porcentaje'
    FIXED = 'fixed', 'Monto Fijo'


# ============================================
# MODELOS PRINCIPALES
# ============================================

class ProductCategory(models.Model):
    """Categorías de productos con soporte para anidación"""
    name = models.CharField('Nombre', max_length=100)
    code = models.CharField('Código', max_length=20, unique=True, blank=True, null=True)
    description = models.TextField('Descripción', blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='subcategories',
        null=True,
        blank=True,
        verbose_name='Categoría Padre'
    )
    is_active = models.BooleanField('Activo', default=True)
    created_at = models.DateTimeField('Creado', auto_now_add=True)
    updated_at = models.DateTimeField('Actualizado', auto_now=True)

    class Meta:
        verbose_name = 'Categoría de Producto'
        verbose_name_plural = 'Categorías de Productos'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Modelo principal de productos (Producto Base/Maestro)
    Este representa el producto genérico. Las variaciones de presentación
    se manejan en el modelo ProductPresentation.
    """
    
    # Identificación
    sku = models.CharField('SKU Base', max_length=50, unique=True, db_index=True)
    internal_code = models.CharField('Código Interno', max_length=50, blank=True, null=True)
    
    # Información básica
    name = models.CharField('Nombre', max_length=255)
    description = models.TextField('Descripción', blank=True)
    short_description = models.CharField('Descripción Corta', max_length=255, blank=True)
    type = models.CharField('Tipo', max_length=20, choices=ProductType.choices, default=ProductType.PRODUCT)
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name='Categoría'
    )
    brand = models.CharField('Marca', max_length=100, blank=True)
    
    # Indica si el producto maneja múltiples presentaciones
    has_presentations = models.BooleanField('Tiene Presentaciones', default=False)
    
    # Precios base (se usan si NO tiene presentaciones)
    cost = models.DecimalField(
        'Costo Base',
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Usado solo si no tiene presentaciones'
    )
    base_price = models.DecimalField(
        'Precio Base',
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Usado solo si no tiene presentaciones'
    )
    wholesale_price = models.DecimalField(
        'Precio Mayorista Base',
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Usado solo si no tiene presentaciones'
    )
    retail_price = models.DecimalField(
        'Precio Minorista Base',
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Usado solo si no tiene presentaciones'
    )
    discount_price = models.DecimalField(
        'Precio con Descuento Base',
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Usado solo si no tiene presentaciones'
    )
    
    # Configuración de precios
    currency = models.CharField('Moneda', max_length=3, default='COP')  # ISO 4217
    profit_margin = models.DecimalField(
        'Margen de Ganancia (%)',
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))]
    )
    price_includes_tax = models.BooleanField('Precio Incluye Impuestos', default=True)
    
    # Unidad base (se hereda a presentaciones si no se especifica)
    unit_of_measure = models.CharField(
        'Unidad de Medida Base',
        max_length=20,
        choices=UnitOfMeasure.choices,
        default=UnitOfMeasure.UNIT
    )
    
    # Inventario base (se usa si NO tiene presentaciones)
    current_stock = models.DecimalField(
        'Stock Actual',
        max_digits=15,
        decimal_places=3,
        default=Decimal('0.000'),
        help_text='Usado solo si no tiene presentaciones'
    )
    min_stock = models.DecimalField(
        'Stock Mínimo',
        max_digits=15,
        decimal_places=3,
        default=Decimal('0.000'),
        help_text='Usado solo si no tiene presentaciones'
    )
    max_stock = models.DecimalField(
        'Stock Máximo',
        max_digits=15,
        decimal_places=3,
        null=True,
        blank=True,
        help_text='Usado solo si no tiene presentaciones'
    )
    reorder_point = models.DecimalField(
        'Punto de Reorden',
        max_digits=15,
        decimal_places=3,
        null=True,
        blank=True,
        help_text='Usado solo si no tiene presentaciones'
    )
    reserved_stock = models.DecimalField(
        'Stock Reservado',
        max_digits=15,
        decimal_places=3,
        default=Decimal('0.000'),
        help_text='Usado solo si no tiene presentaciones'
    )
    
    # Ubicación base
    warehouse = models.CharField('Bodega', max_length=100, blank=True)
    location = models.CharField('Ubicación', max_length=100, blank=True)
    
    # Configuración de inventario
    track_inventory = models.BooleanField('Trackear Inventario', default=True)
    allow_negative_stock = models.BooleanField('Permitir Stock Negativo', default=False)
    
    # Fechas de inventario
    last_restock_date = models.DateTimeField('Última Reposición', null=True, blank=True)
    next_restock_date = models.DateTimeField('Próxima Reposición', null=True, blank=True)
    
    # Estado
    status = models.CharField(
        'Estado',
        max_length=20,
        choices=ProductStatus.choices,
        default=ProductStatus.ACTIVE
    )
    is_active = models.BooleanField('Activo', default=True, db_index=True)
    
    # Configuración de ventas
    allow_decimal_quantity = models.BooleanField('Permitir Cantidad Decimal', default=False)
    requires_serial_number = models.BooleanField('Requiere Número de Serie', default=False)
    has_batches = models.BooleanField('Maneja Lotes', default=False)
    has_expiration = models.BooleanField('Maneja Vencimiento', default=False)
    
    # Metadata
    tags = models.CharField('Etiquetas', max_length=500, blank=True, help_text='Separadas por comas')
    notes = models.TextField('Notas', blank=True)
    
    # Auditoría
    created_at = models.DateTimeField('Creado', auto_now_add=True)
    updated_at = models.DateTimeField('Actualizado', auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='products_created',
        verbose_name='Creado Por'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products_updated',
        verbose_name='Actualizado Por'
    )

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['is_active', 'status']),
            models.Index(fields=['category', 'is_active']),
        ]

    def __str__(self):
        return f"{self.sku} - {self.name}"

    @property
    def available_stock(self):
        """
        Calcula el stock disponible total.
        Si tiene presentaciones, suma el stock de todas ellas.
        Si no, usa el stock propio.
        """
        if self.has_presentations:
            total = Decimal('0.000')
            for presentation in self.presentations.filter(is_active=True):
                total += presentation.available_stock
            return total
        return self.current_stock - self.reserved_stock

    @property
    def needs_restock(self):
        """Verifica si necesita reposición"""
        if self.has_presentations:
            # Si alguna presentación activa necesita reposición
            return any(p.needs_restock for p in self.presentations.filter(is_active=True))
        
        if self.reorder_point:
            return self.available_stock <= self.reorder_point
        return self.available_stock <= self.min_stock

    def get_tags_list(self):
        """Retorna las etiquetas como lista"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []

    def calculate_profit_margin(self):
        """Calcula el margen de ganancia actual"""
        if self.has_presentations:
            # Retorna el margen promedio de las presentaciones activas
            presentations = self.presentations.filter(is_active=True)
            if presentations.exists():
                margins = [p.calculate_profit_margin() for p in presentations if p.cost > 0]
                if margins:
                    return sum(margins) / len(margins)
            return Decimal('0.00')
        
        if self.cost > 0:
            return ((self.base_price - self.cost) / self.cost) * 100
        return Decimal('0.00')


class ProductPresentation(models.Model):
    """
    Presentaciones de productos - Diferentes formatos/tamaños del mismo producto
    Ejemplos: 
    - Coca Cola: 250ml, 500ml, 1L, 2L, 3L
    - Aceite: 100ml, 250ml, 500ml, 1L
    - Cemento: Bolsa 25kg, Bulto 50kg
    - Cables: Metro, Rollo 100m
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='presentations',
        verbose_name='Producto Base'
    )
    
    # Identificación única de la presentación
    sku = models.CharField('SKU', max_length=50, unique=True, db_index=True)
    barcode = models.CharField('Código de Barras', max_length=50, blank=True, null=True, db_index=True)
    internal_code = models.CharField('Código Interno', max_length=50, blank=True, null=True)
    
    # Descripción de la presentación
    name = models.CharField('Nombre de Presentación', max_length=255, help_text='Ej: Botella 500ml, Caja x12, Granel')
    description = models.TextField('Descripción', blank=True)
    
    # Unidad y cantidad
    unit_of_measure = models.CharField(
        'Unidad de Medida',
        max_length=20,
        choices=UnitOfMeasure.choices,
        help_text='Unidad en que se vende esta presentación'
    )
    content_quantity = models.DecimalField(
        'Cantidad de Contenido',
        max_digits=15,
        decimal_places=3,
        default=Decimal('1.000'),
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text='Ej: 500 (para 500ml), 12 (para caja de 12 unidades)'
    )
    content_unit = models.CharField(
        'Unidad del Contenido',
        max_length=20,
        choices=UnitOfMeasure.choices,
        blank=True,
        help_text='Ej: ML para 500ml, UNIT para caja de 12 unidades'
    )
    unit_label = models.CharField(
        'Etiqueta de Presentación',
        max_length=100,
        blank=True,
        help_text='Ej: Botella 500ml, Caja x12 unidades, Saco 50kg'
    )
    
    # Factor de conversión a unidad base
    conversion_factor = models.DecimalField(
        'Factor de Conversión',
        max_digits=15,
        decimal_places=6,
        default=Decimal('1.000000'),
        validators=[MinValueValidator(Decimal('0.000001'))],
        help_text='Cantidad de unidades base que representa. Ej: Caja de 12 = 12'
    )
    
    # Precios específicos de esta presentación
    cost = models.DecimalField(
        'Costo',
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    base_price = models.DecimalField(
        'Precio Base',
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    wholesale_price = models.DecimalField(
        'Precio Mayorista',
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    retail_price = models.DecimalField(
        'Precio Minorista',
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    discount_price = models.DecimalField(
        'Precio con Descuento',
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    # Inventario específico
    current_stock = models.DecimalField(
        'Stock Actual',
        max_digits=15,
        decimal_places=3,
        default=Decimal('0.000')
    )
    min_stock = models.DecimalField(
        'Stock Mínimo',
        max_digits=15,
        decimal_places=3,
        default=Decimal('0.000')
    )
    max_stock = models.DecimalField(
        'Stock Máximo',
        max_digits=15,
        decimal_places=3,
        null=True,
        blank=True
    )
    reorder_point = models.DecimalField(
        'Punto de Reorden',
        max_digits=15,
        decimal_places=3,
        null=True,
        blank=True
    )
    reserved_stock = models.DecimalField(
        'Stock Reservado',
        max_digits=15,
        decimal_places=3,
        default=Decimal('0.000')
    )
    
    # Ubicación específica
    warehouse = models.CharField('Bodega', max_length=100, blank=True)
    location = models.CharField('Ubicación', max_length=100, blank=True)
    
    # Peso y dimensiones (útil para logística)
    weight = models.DecimalField(
        'Peso (kg)',
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True
    )
    length = models.DecimalField(
        'Largo (cm)',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    width = models.DecimalField(
        'Ancho (cm)',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    height = models.DecimalField(
        'Alto (cm)',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Configuración
    is_default = models.BooleanField(
        'Presentación por Defecto',
        default=False,
        help_text='Presentación que se muestra por defecto'
    )
    is_active = models.BooleanField('Activo', default=True, db_index=True)
    allow_fractional_sale = models.BooleanField(
        'Permitir Venta Fraccionada',
        default=False,
        help_text='Permite vender fracciones de esta presentación'
    )
    
    # Orden de visualización
    display_order = models.PositiveIntegerField('Orden', default=0)
    
    # Control de lotes y series
    requires_serial_number = models.BooleanField('Requiere Número de Serie', default=False)
    has_batches = models.BooleanField('Maneja Lotes', default=False)
    has_expiration = models.BooleanField('Maneja Vencimiento', default=False)
    
    # Metadata
    notes = models.TextField('Notas', blank=True)
    
    # Auditoría
    created_at = models.DateTimeField('Creado', auto_now_add=True)
    updated_at = models.DateTimeField('Actualizado', auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='presentations_created',
        verbose_name='Creado Por'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='presentations_updated',
        verbose_name='Actualizado Por'
    )

    class Meta:
        verbose_name = 'Presentación de Producto'
        verbose_name_plural = 'Presentaciones de Productos'
        ordering = ['product', 'display_order', 'name']
        unique_together = [['product', 'name']]
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['barcode']),
            models.Index(fields=['product', 'is_active']),
            models.Index(fields=['product', 'is_default']),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.name}"

    @property
    def full_name(self):
        """Nombre completo incluyendo producto y presentación"""
        return f"{self.product.name} ({self.name})"

    @property
    def available_stock(self):
        """Calcula el stock disponible (actual - reservado)"""
        return self.current_stock - self.reserved_stock

    @property
    def needs_restock(self):
        """Verifica si necesita reposición"""
        if self.reorder_point:
            return self.available_stock <= self.reorder_point
        return self.available_stock <= self.min_stock

    @property
    def stock_in_base_units(self):
        """Calcula el stock en unidades base del producto"""
        return self.current_stock * self.conversion_factor

    def calculate_profit_margin(self):
        """Calcula el margen de ganancia"""
        if self.cost > 0:
            return ((self.base_price - self.cost) / self.cost) * 100
        return Decimal('0.00')

    def calculate_price_per_unit(self):
        """Calcula el precio por unidad de contenido"""
        if self.content_quantity > 0:
            return self.base_price / self.content_quantity
        return self.base_price

    def save(self, *args, **kwargs):
        # Si es presentación por defecto, quitar flag de otras presentaciones
        if self.is_default:
            ProductPresentation.objects.filter(
                product=self.product,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        
        # Marcar que el producto tiene presentaciones
        if not self.product.has_presentations:
            self.product.has_presentations = True
            self.product.save(update_fields=['has_presentations'])
        
        super().save(*args, **kwargs)


class PresentationTax(models.Model):
    """Impuestos específicos para presentaciones (si difieren del producto base)"""
    presentation = models.ForeignKey(
        ProductPresentation,
        on_delete=models.CASCADE,
        related_name='taxes',
        verbose_name='Presentación'
    )
    tax_type = models.CharField('Tipo de Impuesto', max_length=20, choices=TaxType.choices)
    name = models.CharField('Nombre', max_length=100, help_text='Ej: IVA 19%')
    rate = models.DecimalField(
        'Tasa (%)',
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))]
    )
    is_included = models.BooleanField('Incluido en Precio', default=True)
    tax_base = models.DecimalField(
        'Base Gravable',
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Opcional, si es diferente del precio'
    )
    is_active = models.BooleanField('Activo', default=True)

    class Meta:
        verbose_name = 'Impuesto de Presentación'
        verbose_name_plural = 'Impuestos de Presentaciones'
        ordering = ['presentation', 'tax_type']

    def __str__(self):
        return f"{self.presentation.sku} - {self.name}"

    def calculate_tax_amount(self, base_amount):
        """Calcula el monto del impuesto sobre un monto base"""
        return (base_amount * self.rate) / 100


class PresentationVolumePricing(models.Model):
    """Precios por volumen para presentaciones específicas"""
    presentation = models.ForeignKey(
        ProductPresentation,
        on_delete=models.CASCADE,
        related_name='volume_pricing',
        verbose_name='Presentación'
    )
    min_quantity = models.DecimalField(
        'Cantidad Mínima',
        max_digits=15,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))]
    )
    max_quantity = models.DecimalField(
        'Cantidad Máxima',
        max_digits=15,
        decimal_places=3,
        null=True,
        blank=True
    )
    price = models.DecimalField(
        'Precio',
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    is_active = models.BooleanField('Activo', default=True)

    class Meta:
        verbose_name = 'Precio por Volumen de Presentación'
        verbose_name_plural = 'Precios por Volumen de Presentaciones'
        ordering = ['presentation', 'min_quantity']

    def __str__(self):
        max_qty = self.max_quantity if self.max_quantity else '∞'
        return f"{self.presentation.sku}: {self.min_quantity}-{max_qty} = ${self.price}"


class ProductTax(models.Model):
    """Impuestos aplicables a productos base (heredados a presentaciones si no se especifica)"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='taxes',
        verbose_name='Producto'
    )
    tax_type = models.CharField('Tipo de Impuesto', max_length=20, choices=TaxType.choices)
    name = models.CharField('Nombre', max_length=100, help_text='Ej: IVA 19%')
    rate = models.DecimalField(
        'Tasa (%)',
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))]
    )
    is_included = models.BooleanField('Incluido en Precio', default=True)
    tax_base = models.DecimalField(
        'Base Gravable',
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Opcional, si es diferente del precio'
    )
    is_active = models.BooleanField('Activo', default=True)

    class Meta:
        verbose_name = 'Impuesto de Producto'
        verbose_name_plural = 'Impuestos de Productos'
        ordering = ['product', 'tax_type']

    def __str__(self):
        return f"{self.product.sku} - {self.name}"

    def calculate_tax_amount(self, base_amount):
        """Calcula el monto del impuesto sobre un monto base"""
        return (base_amount * self.rate) / 100


class VolumePricing(models.Model):
    """Precios por volumen para productos"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='volume_pricing',
        verbose_name='Producto'
    )
    min_quantity = models.DecimalField(
        'Cantidad Mínima',
        max_digits=15,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))]
    )
    max_quantity = models.DecimalField(
        'Cantidad Máxima',
        max_digits=15,
        decimal_places=3,
        null=True,
        blank=True
    )
    price = models.DecimalField(
        'Precio',
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    is_active = models.BooleanField('Activo', default=True)

    class Meta:
        verbose_name = 'Precio por Volumen'
        verbose_name_plural = 'Precios por Volumen'
        ordering = ['product', 'min_quantity']

    def __str__(self):
        max_qty = self.max_quantity if self.max_quantity else '∞'
        return f"{self.product.sku}: {self.min_quantity}-{max_qty} = ${self.price}"


class ProductImage(models.Model):
    """Imágenes de productos"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Producto'
    )
    image = models.ImageField('Imagen', upload_to='products/%Y/%m/')
    thumbnail = models.ImageField('Miniatura', upload_to='products/thumbnails/%Y/%m/', blank=True, null=True)
    alt_text = models.CharField('Texto Alternativo', max_length=255, blank=True)
    is_primary = models.BooleanField('Imagen Principal', default=False)
    order = models.PositiveIntegerField('Orden', default=0)
    created_at = models.DateTimeField('Creado', auto_now_add=True)

    class Meta:
        verbose_name = 'Imagen de Producto'
        verbose_name_plural = 'Imágenes de Productos'
        ordering = ['product', 'order', 'is_primary']

    def __str__(self):
        return f"{self.product.sku} - Imagen {self.order}"

    def save(self, *args, **kwargs):
        # Si es imagen principal, quitar flag de otras imágenes
        if self.is_primary:
            ProductImage.objects.filter(product=self.product, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)


# ============================================
# MODELOS PARA FACTURACIÓN
# ============================================

## Modelos de facturación se definen en app 'facturas'.
