from django.db import models

class Cliente(models.Model):
    """
    Modelo para gestionar la información de los clientes del sistema
    """
    TIPO_CLIENTE = [
        ('natural', 'Persona Natural'),
        ('juridica', 'Persona Jurídica'),
    ]
    
    ESTADO_CLIENTE = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('suspendido', 'Suspendido'),
    ]
    
    # Información básica
    codigo = models.CharField(max_length=20, unique=True, verbose_name='Código')
    nombre = models.CharField(max_length=200, verbose_name='Nombre o Razón Social')
    tipo = models.CharField(max_length=10, choices=TIPO_CLIENTE, default='natural', verbose_name='Tipo')
    
    # Información de contacto
    ruc_dni = models.CharField(max_length=20, unique=True, verbose_name='RUC/DNI')
    direccion = models.TextField(verbose_name='Dirección')
    telefono = models.CharField(max_length=20, verbose_name='Teléfono')
    email = models.EmailField(verbose_name='Email', blank=True)
    
    # Información comercial
    limite_credito = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0, 
        verbose_name='Límite de Crédito'
    )
    estado = models.CharField(
        max_length=10, 
        choices=ESTADO_CLIENTE, 
        default='activo', 
        verbose_name='Estado'
    )
    
    # Auditoría
    fecha_creacion = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='Fecha de Creación'
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True, 
        verbose_name='Fecha de Actualización'
    )
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
