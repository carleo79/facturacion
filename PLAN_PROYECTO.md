# Plan del Proyecto: Sistema de Facturación con Django y PostgreSQL

## 📋 Descripción General
Sistema completo de facturación con gestión de inventario, compras, kardex y múltiples presentaciones de productos.

## 🏗️ Arquitectura del Sistema

### Aplicaciones Django Creadas:
- `clientes` - Gestión de información de clientes
- `productos` - Catálogo de productos base
- `presentaciones` - Diferentes presentaciones para cada producto
- `inventario` - Control de stock y existencias
- `compras` - Registro de compras a proveedores
- `kardex` - Movimientos de inventario (entradas/salidas)
- `facturas` - Emisión de facturas de venta
- `usuarios` - Sistema de autenticación y permisos

## 📊 Modelos de Datos Principales

### 1. Modelo Clientes
- Información básica (nombre, dirección, contacto)
- Tipo de cliente (natural/jurídico)
- Límite de crédito
- Estado del cliente

### 2. Modelo Productos
- Código y descripción
- Categorías y subcategorías
- Precio base
- Impuestos aplicables

### 3. Modelo Presentaciones (Relación con Productos)
- Un producto puede tener múltiples presentaciones
- Cada presentación con: unidad de medida, factor de conversión, precio específico
- Ejemplo: Leche → Presentaciones: Botella 1L, Caja 12 unidades, Galón

### 4. Modelo Inventario
- Stock actual por presentación
- Stock mínimo y máximo
- Ubicación en bodega

### 5. Modelo Compras
- Registro de compras a proveedores
- Detalle de items comprados
- Precios de compra

### 6. Modelo Kardex (Corazón del Sistema)
- Movimientos de entrada (compras, ajustes positivos)
- Movimientos de salida (ventas, ajustes negativos)
- Saldo actualizado después de cada movimiento
- Costo promedio ponderado

### 7. Modelo Facturas
- Cabecera de factura (cliente, fecha, total)
- Detalle de items vendidos
- Impuestos y descuentos
- Estado de la factura

## 🔄 Flujos de Trabajo

### Flujo de Compras:
1. Registro de compra → 2. Actualización de Kardex (entrada) → 3. Actualización de Inventario

### Flujo de Ventas:
1. Creación de factura → 2. Validación de stock → 3. Actualización de Kardex (salida) → 4. Actualización de Inventario

### Flujo de Kardex:
- Registra cada movimiento con: fecha, tipo, cantidad, costo, saldo
- Calcula costo promedio automáticamente

## 🗓️ Cronograma de Implementación

### Fase 1: Configuración Inicial ✅
- [x] Crear proyecto Django
- [x] Crear aplicaciones necesarias

### Fase 2: Base de datos y Modelos
- [ ] Configurar PostgreSQL
- [ ] Crear modelos Clientes y Productos
- [ ] Crear modelo Presentaciones
- [ ] Crear modelos Inventario y Kardex
- [ ] Crear modelos Compras y Facturas

### Fase 3: Vistas y Templates
- [ ] CRUD para Clientes
- [ ] CRUD para Productos y Presentaciones
- [ ] Gestión de Inventario
- [ ] Módulo de Compras
- [ ] Módulo de Facturación

### Fase 4: Funcionalidades Avanzadas
- [ ] Sistema de autenticación
- [ ] Reportes y estadísticas
- [ ] Integración de impuestos
- [ ] Validaciones de negocio

## 🛠️ Tecnologías Utilizadas
- **Backend**: Django 5.2.7
- **Base de datos**: PostgreSQL
- **Frontend**: HTML5, CSS3, JavaScript (vanilla)
- **Templates**: Django Template Language
- **Autenticación**: Django Auth System

## 📈 Funcionalidades Clave
- ✅ Gestión de productos con múltiples presentaciones
- ✅ Control de inventario con kardex
- ✅ Sistema completo de compras y ventas
- ✅ Facturación electrónica
- ✅ Reportes de movimientos
- ✅ Dashboard administrativo

## 🔐 Seguridad y Permisos
- Roles de usuario: Administrador, Vendedor, Almacén
- Permisos granular por módulo
- Historial de cambios críticos

---
*Este documento se actualizará durante el desarrollo del proyecto*
