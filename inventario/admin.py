from django.contrib import admin
from .models import Warehouse, StockItem, InventoryAdjustment


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "address", "is_active")
    search_fields = ("code", "name")
    list_filter = ("is_active",)


@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    list_display = ("warehouse", "presentation", "quantity", "reserved_quantity", "available_quantity", "location", "is_active")
    search_fields = ("warehouse__code", "presentation__sku")
    list_filter = ("warehouse", "is_active")


@admin.register(InventoryAdjustment)
class InventoryAdjustmentAdmin(admin.ModelAdmin):
    list_display = ("created_at", "warehouse", "presentation", "adjustment_type", "quantity", "reason")
    list_filter = ("adjustment_type", "warehouse")
    search_fields = ("presentation__sku", "warehouse__code", "reason", "reference")
