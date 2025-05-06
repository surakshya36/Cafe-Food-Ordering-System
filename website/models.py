from django.db import models
from django.conf import settings
from menuitems.models import MenuItem

class Cart(models.Model):
    """Session-based shopping cart for website"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'session_key')
    
    @property
    def total_items(self):
        return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0
    
    @property
    def subtotal(self):
        return sum(item.subtotal for item in self.items.all())
    
    def __str__(self):
        if self.user:
            return f"Cart for {self.user.email}"
        return f"Anonymous Cart ({self.session_key})"
    
    def clear(self):
        """Empty the cart"""
        self.items.all().delete()
    
    def create_order(self, order_data):
        """Convert cart to an actual order in the backend system"""
        from orders.models import Order, OrderItem
        
        order = Order.objects.create(
            table=order_data['table'],
            customer_name=order_data.get('customer_name', ''),
            special_requests=order_data.get('special_requests', ''),
            vip_discount=order_data.get('vip_discount', 0),
            status='CONFIRMED'
        )
        
        for cart_item in self.items.all():
            OrderItem.objects.create(
                order=order,
                menu_item=cart_item.menu_item,
                quantity=cart_item.quantity,
                unit_price=cart_item.menu_item.price,
                special_requests=cart_item.special_requests
            )
        
        order.update_total()
        self.clear()
        return order

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    special_requests = models.TextField(blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def subtotal(self):
        return self.menu_item.price * self.quantity
    
    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name}"
    
    def increase_quantity(self, amount=1):
        self.quantity += amount
        self.save()
    
    def decrease_quantity(self, amount=1):
        self.quantity = max(1, self.quantity - amount)
        self.save()