from django.contrib import admin
from .models import Invoice, InvoicePayment, InvoiceLineItem, LineItemTax


class LineItemTaxInline(admin.TabularInline):
    model = LineItemTax
    extra = 0


class InvoiceLineItemInline(admin.TabularInline):
    model = InvoiceLineItem
    extra = 0
    inlines = [LineItemTaxInline]


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("number", "date", "customer", "warehouse", "status", "total")
    list_filter = ("status", "warehouse")
    search_fields = ("number", "customer__nombre", "customer__codigo")
    inlines = [InvoiceLineItemInline]


@admin.register(InvoicePayment)
class InvoicePaymentAdmin(admin.ModelAdmin):
    list_display = ("invoice", "method", "amount", "received_at")
    list_filter = ("method",)
    search_fields = ("invoice__number", "reference")


@admin.register(InvoiceLineItem)
class InvoiceLineItemAdmin(admin.ModelAdmin):
    list_display = ("invoice", "sku", "name", "quantity", "unit_price", "total")
    search_fields = ("invoice__number", "sku", "name")


@admin.register(LineItemTax)
class LineItemTaxAdmin(admin.ModelAdmin):
    list_display = ("line_item", "name", "tax_type", "rate", "amount")
