from django.db import models
from django.utils import timezone

class Order(models.Model):
    ORDER_STATUS = (
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('PREPARING', 'Preparing'),
        ('READY', 'Ready to Serve'),
        ('SERVED', 'Served'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled'),
    )

    table = models.ForeignKey('tables.Table', on_delete=models.PROTECT, related_name='orders')
    customer_name = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=15, choices=ORDER_STATUS, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    special_requests = models.TextField(blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)
    vip_discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # ✅ New Field
    is_rush = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.table} ({self.get_status_display()})"

    def update_total(self):
        subtotal = sum(item.subtotal for item in self.items.all())
        self.total_amount = max(0, subtotal - self.vip_discount)
        self.save(update_fields=['total_amount'])

    def close_order(self):
        self.status = 'PAID'
        self.is_paid = True
        self.save()
        
        if self.table.current_order == self:
            self.table.current_order = None
            self.table.status = 'AVAILABLE'
            self.table.save()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey('menuitems.MenuItem', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    special_requests = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
    
    @property
    def subtotal(self):
        return self.unit_price * self.quantity
        
    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name} (Order #{self.order.id})"
    
    def save(self, *args, **kwargs):
        if not self.unit_price:
            self.unit_price = self.menu_item.price
        super().save(*args, **kwargs)
        self.order.update_total()