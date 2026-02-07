from django.contrib import admin
from .models import Supplier, PurchaseOrder, PurchaseOrderItem


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 0


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "tax_id", "phone", "email", "is_active")
    search_fields = ("code", "name", "tax_id")
    list_filter = ("is_active",)


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ("number", "supplier", "warehouse", "status", "order_date", "total")
    list_filter = ("status", "warehouse", "supplier")
    search_fields = ("number", "supplier__name", "supplier__tax_id")
    inlines = [PurchaseOrderItemInline]
