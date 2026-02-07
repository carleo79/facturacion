from django.contrib import admin
from .models import KardexEntry


@admin.register(KardexEntry)
class KardexEntryAdmin(admin.ModelAdmin):
    list_display = ("date", "warehouse", "presentation", "movement_type", "qty_in", "qty_out", "balance_qty", "average_cost")
    list_filter = ("movement_type", "warehouse")
    search_fields = ("presentation__sku", "warehouse__code", "reference")
