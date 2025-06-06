from django.db import models
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP

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
    ORDER_TYPES = (
        ('normal', 'Normal'),
        ('vip', 'VIP'),
    )
    order_type = models.CharField(max_length=10, choices=ORDER_TYPES, default='normal')
    session_key = models.CharField(max_length=40, blank=True, null=True) 
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
    
    @property
    def original_subtotal(self):
        """Returns the cart total before any discounts"""
        return sum(item.subtotal for item in self.items.all())
    
    @property
    def subtotal_after_discount(self):
        """Returns the amount after discount is applied"""
        return self.original_subtotal - self.calculate_vip_discount()
    
    @property
    def vat_amount(self):
        """Calculates VAT on the discounted subtotal"""
        return (self.subtotal_after_discount * Decimal('0.13')).quantize(Decimal('0.01'))
    
    @property
    def service_charge(self):
        """Calculates service charge on the discounted subtotal"""
        if self.order_type == 'vip':
            rate = Decimal('0.25') if self.is_rush else Decimal('0.20')
        else:
            rate = Decimal('0.15') if self.is_rush else Decimal('0.10')
        return (self.subtotal_after_discount * rate).quantize(Decimal('0.01'))
    
    @property
    def calculated_total(self):
        """Calculates what the total should be based on current items"""
        return (self.subtotal_after_discount + self.vat_amount + self.service_charge).quantize(Decimal('0.01'))
    
    def update_total(self):
        """Updates the total_amount field to match the calculated total"""
        new_total = self.calculated_total
        if self.total_amount != new_total:
            self.total_amount = new_total
            self.save(update_fields=['total_amount'])
    
    def calculate_vip_discount(self):
        subtotal = self.original_subtotal
        
        if self.order_type == 'vip':
            # VIP discount structure
            if subtotal < 1000:
                return Decimal('0.00')
            elif subtotal <= 3000:
                return subtotal * Decimal('0.03')
            elif subtotal <= 6000:
                return subtotal * Decimal('0.06')
            else:
                return subtotal * Decimal('0.10')
        else:
            # Normal order discount structure
            if subtotal < 500:
                return Decimal('0.00')
            elif subtotal <= 1000:
                return subtotal * Decimal('0.02')
            elif subtotal <= 5000:
                return subtotal * Decimal('0.05')
            else:
                return subtotal * Decimal('0.10')

    def close_order(self):
        self.status = 'PAID'
        self.is_paid = True
        self.save()
        
        if self.table.current_order == self:
            self.table.current_order = None
            self.table.status = 'AVAILABLE'
            self.table.save()

    @property
    def total_paid(self):
        return sum(p.amount for p in self.payments.filter(status='COMPLETED'))

    @property
    def remaining_due(self):
        return max(self.calculated_total - self.total_paid, 0)

    def check_and_close_if_paid(self):
        if self.remaining_due == 0 and not self.is_paid:
            self.close_order()



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey('menuitems.MenuItem', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    special_requests = models.TextField(blank=True, null=True)
    
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