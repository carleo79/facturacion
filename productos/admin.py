from django.contrib import admin
from .models import (
    ProductCategory,
    Product,
    ProductPresentation,
    ProductTax,
    PresentationTax,
    VolumePricing,
    PresentationVolumePricing,
    ProductImage,
)


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "parent", "is_active")
    search_fields = ("name", "code")
    list_filter = ("is_active",)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


class ProductPresentationInline(admin.TabularInline):
    model = ProductPresentation
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "category", "is_active", "status", "has_presentations")
    list_filter = ("is_active", "status", "category")
    search_fields = ("sku", "name", "tags", "brand")
    inlines = [ProductPresentationInline, ProductImageInline]
    exclude = ("created_by", "updated_by")

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            # Para inlines de presentaciones, setear auditoría
            if hasattr(instance, 'created_by') and not instance.created_by:
                instance.created_by = request.user
            if hasattr(instance, 'updated_by'):
                instance.updated_by = request.user
            instance.save()
        formset.save_m2m()


@admin.register(ProductPresentation)
class ProductPresentationAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "product", "unit_of_measure", "base_price", "is_active", "is_default")
    list_filter = ("is_active", "is_default", "unit_of_measure")
    search_fields = ("sku", "name", "product__name")
    exclude = ("created_by", "updated_by")

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ProductTax)
class ProductTaxAdmin(admin.ModelAdmin):
    list_display = ("product", "name", "tax_type", "rate", "is_included", "is_active")
    list_filter = ("tax_type", "is_included", "is_active")
    search_fields = ("product__sku", "product__name", "name")


@admin.register(PresentationTax)
class PresentationTaxAdmin(admin.ModelAdmin):
    list_display = ("presentation", "name", "tax_type", "rate", "is_included", "is_active")
    list_filter = ("tax_type", "is_included", "is_active")
    search_fields = ("presentation__sku", "presentation__name", "name")


@admin.register(VolumePricing)
class VolumePricingAdmin(admin.ModelAdmin):
    list_display = ("product", "min_quantity", "max_quantity", "price", "is_active")
    list_filter = ("is_active",)
    search_fields = ("product__sku", "product__name")


@admin.register(PresentationVolumePricing)
class PresentationVolumePricingAdmin(admin.ModelAdmin):
    list_display = ("presentation", "min_quantity", "max_quantity", "price", "is_active")
    list_filter = ("is_active",)
    search_fields = ("presentation__sku", "presentation__name")


