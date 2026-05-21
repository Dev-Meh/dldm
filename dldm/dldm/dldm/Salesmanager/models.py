from django.db import models
from django.conf import settings

class Drug(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Inventory(models.Model):
    # Per–sales-manager inventory: each manager has their own stock per drug
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE, related_name='inventories')
    sales_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inventories'
    )
    quantity = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=10)
    last_restocked = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.sales_manager:
            return f"{self.drug.name} - {self.quantity} units (by {self.sales_manager.username})"
        return f"{self.drug.name} - {self.quantity} units"

    @property
    def status(self):
        if self.quantity <= 0:
            return 'out_of_stock'
        elif self.quantity <= self.reorder_level:
            return 'low_stock'
        return 'in_stock'

    @property
    def status_color(self):
        status_colors = {
            'out_of_stock': 'danger',
            'low_stock': 'warning',
            'in_stock': 'success'
        }
        return status_colors.get(self.status, 'secondary')

    class Meta:
        unique_together = ('drug', 'sales_manager')

class Sale(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]

    order_id = models.CharField(max_length=50, db_index=True)
    customer_name = models.CharField(max_length=200)
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE, related_name='sales')
    quantity = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    date = models.DateTimeField(auto_now_add=True)
    sales_manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='sales')

    def __str__(self):
        return f"Order {self.order_id} - {self.customer_name}"

    def save(self, *args, **kwargs):
        if not self.order_id:
            # Generate unique order ID
            last_order = Sale.objects.order_by('-id').first()
            last_id = last_order.id if last_order else 0
            self.order_id = f"ORD{str(last_id + 1).zfill(6)}"
        super().save(*args, **kwargs)

    @property
    def status_color(self):
        status_colors = {
            'pending': 'warning',
            'completed': 'success',
            'cancelled': 'danger'
        }
        return status_colors.get(self.status, 'secondary')

class SalesReport(models.Model):
    REPORT_TYPES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly')
    ]

    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    total_sales = models.DecimalField(max_digits=10, decimal_places=2)
    total_orders = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.get_report_type_display()} Report - {self.start_date} to {self.end_date}"

    class Meta:
        ordering = ['-created_at']
