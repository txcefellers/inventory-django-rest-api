from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    InventoryTransactionViewSet,
    LowStockAlertView,
    ProductViewSet,
    StockViewSet,
    SupplierViewSet,
)

router = DefaultRouter()
router.register("suppliers", SupplierViewSet, basename="supplier")
router.register("products", ProductViewSet, basename="product")
router.register("stocks", StockViewSet, basename="stock")
router.register("transactions", InventoryTransactionViewSet, basename="transaction")

urlpatterns = [
    path("", include(router.urls)),
    path("low-stock-alerts/", LowStockAlertView.as_view(), name="low-stock-alerts"),
]
