from django.db import models
from django.utils import timezone

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
    
    # Payment identification
    payment_reference = models.CharField(max_length=100, null=True, blank=True)

    transaction_id  = models.CharField(max_length=100, blank=True)
    
    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=10, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=15, choices=PAYMENT_STATUS, default='PENDING')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at  = models.DateTimeField(null=True, blank=True)
    
    # Additional information
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Payment {self.payment_reference} ({self.get_status_display()})"
    
    def mark_as_completed(self):
        self.status = 'COMPLETED'
        self.processed_at = timezone.now()
        self.save()
    
    def mark_as_failed(self, reason=""):
        self.status = 'FAILED'
        self.notes = f"Failed: {reason}"
        self.save()

class OrderPayment(models.Model):
    """Linking table between orders and payments (optional)"""
    order_number = models.CharField(max_length=20)  # Reference instead of FK
    payment_reference = models.CharField(max_length=100, null=True, blank=True)

    amount_applied = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('order_number', 'payment_reference')
    
    def __str__(self):
        return f"Order {self.order_number} - Payment {self.payment_reference}"