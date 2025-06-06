from django.db import models
from django.utils import timezone
from orders.models import Order

class Payment(models.Model):
    PAYMENT_METHODS = (
        ('CASH', 'Cash'),
        ('CARD', 'Credit/Debit Card'),
        ('MOBILE', 'Mobile Payment'),
        ('BANK', 'Bank Transfer'),
        ('OTHER', 'Other'),
    )
    
    PAYMENT_STATUS = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
        ('PARTIAL_REFUND', 'Partially Refunded'),
    )
    
    # Direct link to the order
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='payments')

    payment_reference = models.CharField(max_length=100, null=True, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=10, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=15, choices=PAYMENT_STATUS, default='PENDING')

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.payment_reference} for Order #{self.order.id} ({self.get_status_display()})"

    def mark_as_completed(self):
        self.status = 'COMPLETED'
        self.completed_at = timezone.now()
        self.save()

        # Mark the order as paid if the payment covers the total
        if self.amount >= self.order.calculated_total:
            self.order.close_order()

    def mark_as_failed(self, reason=""):
        self.status = 'FAILED'
        self.notes = f"Failed: {reason}"
        self.save()
