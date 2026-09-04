from django.contrib import admin
from .models import InventoryTransaction, Product, Stock, Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone")
    search_fields = ("name", "email", "phone")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "supplier", "unit_price", "reorder_level")
    list_filter = ("supplier",)
    search_fields = ("sku", "name")


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("product", "quantity", "updated_at")
    search_fields = ("product__sku", "product__name")


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ("product", "transaction_type", "quantity", "supplier", "created_at")
    list_filter = ("transaction_type", "supplier")
    search_fields = ("product__sku", "product__name", "supplier__name")
