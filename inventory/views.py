from django.db import transaction
from django.db.models import F, Value
from django.db.models.functions import Coalesce
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import InventoryTransaction, Product, Stock, Supplier
from .serializers import (
    InventoryTransactionSerializer,
    ProductSerializer,
    StockSerializer,
    SupplierSerializer,
)


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("supplier").all()
    serializer_class = ProductSerializer


class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.select_related("product").all()
    serializer_class = StockSerializer


class InventoryTransactionViewSet(viewsets.ModelViewSet):
    queryset = InventoryTransaction.objects.select_related("product", "supplier").all()
    serializer_class = InventoryTransactionSerializer

    @staticmethod
    def _signed_quantity(tx_type: str, quantity: int) -> int:
        if tx_type == InventoryTransaction.IN:
            return quantity
        if tx_type == InventoryTransaction.OUT:
            return -quantity
        return quantity

    @staticmethod
    def _apply_stock_delta(product: Product, delta: int) -> None:
        stock, _ = Stock.objects.get_or_create(product=product, defaults={"quantity": 0})
        new_quantity = stock.quantity + delta
        if new_quantity < 0:
            raise ValidationError(
                {"quantity": f"Insufficient stock for product '{product.sku}'."}
            )
        stock.quantity = new_quantity
        stock.save(update_fields=["quantity", "updated_at"])

    def perform_create(self, serializer):
        with transaction.atomic():
            tx = serializer.save()
            delta = self._signed_quantity(tx.transaction_type, tx.quantity)
            self._apply_stock_delta(tx.product, delta)

    def perform_update(self, serializer):
        with transaction.atomic():
            previous = self.get_object()
            prev_delta = self._signed_quantity(
                previous.transaction_type, previous.quantity
            )
            updated = serializer.save()
            new_delta = self._signed_quantity(updated.transaction_type, updated.quantity)

            if previous.product_id == updated.product_id:
                self._apply_stock_delta(updated.product, new_delta - prev_delta)
            else:
                self._apply_stock_delta(previous.product, -prev_delta)
                self._apply_stock_delta(updated.product, new_delta)

    def perform_destroy(self, instance):
        with transaction.atomic():
            delta = self._signed_quantity(instance.transaction_type, instance.quantity)
            self._apply_stock_delta(instance.product, -delta)
            instance.delete()


class LowStockAlertView(APIView):
    def get(self, request):
        products = (
            Product.objects.select_related("supplier")
            .annotate(current_stock=Coalesce("stock__quantity", Value(0)))
            .filter(current_stock__lte=F("reorder_level"))
            .order_by("name")
        )
        payload = [
            {
                "product_id": product.id,
                "sku": product.sku,
                "name": product.name,
                "supplier": product.supplier.name,
                "current_stock": int(product.current_stock),
                "reorder_level": product.reorder_level,
                "shortage": product.reorder_level - int(product.current_stock),
            }
            for product in products
        ]
        return Response(payload)
