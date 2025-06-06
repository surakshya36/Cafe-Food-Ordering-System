from django.db import models
from django.conf import settings
from menuitems.models import MenuItem
import uuid

class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    completed = models.BooleanField(default=False)
    cart_type = models.CharField(max_length=10, choices=[('normal', 'Normal'), ('vip', 'VIP')], default='normal')
    session_id = models.CharField(max_length=100, null= True, blank=True)

    def __str__(self):
        return str(self.id)
    
    @property
    def total_price(self):
        cartitems = self.cartitems.all()
        total = sum([item.price for item in cartitems])
        return total
      
    @property
    def num_of_items(self):
        cartitems = self.cartitems.all()
        quantity = sum([item.quantity for item in cartitems])
        return quantity


class CartItem(models.Model):
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name="items", null=True, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cartitems")
    quantity = models.IntegerField(default=0)
    special_requests = models.TextField(blank=True, null=True)  
    def __str__(self):
        return self.item.name
    
    @property
    def price(self):
        new_price = self.item.price * self.quantity
        return new_price
