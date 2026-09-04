from django.db import models


class Supplier(models.Model):
    name = models.CharField(max_length=120, unique=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=120)
    sku = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    reorder_level = models.PositiveIntegerField(default=10)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.ForeignKey(
        Supplier, on_delete=models.PROTECT, related_name="products"
    )

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.sku} - {self.name}"


class Stock(models.Model):
    product = models.OneToOneField(
        Product, on_delete=models.CASCADE, related_name="stock"
    )
    quantity = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["product__name"]

    def __str__(self) -> str:
        return f"{self.product.sku}: {self.quantity}"


class InventoryTransaction(models.Model):
    IN = "IN"
    OUT = "OUT"
    ADJUSTMENT = "ADJUSTMENT"
    TRANSACTION_TYPE_CHOICES = [
        (IN, "Stock In"),
        (OUT, "Stock Out"),
        (ADJUSTMENT, "Adjustment"),
    ]

    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="transactions"
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="transactions",
        blank=True,
        null=True,
    )
    transaction_type = models.CharField(max_length=12, choices=TRANSACTION_TYPE_CHOICES)
    quantity = models.PositiveIntegerField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.transaction_type} {self.quantity} x {self.product.sku}"
