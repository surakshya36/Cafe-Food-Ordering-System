from django.db import models
from django.db.models import F

class MenuItem(models.Model):
    VIP_STATUS_CHOICES = (
        ('REGULAR', 'Regular Item'),
        ('VIP_ONLY', 'VIP Exclusive'),
        ('VIP_PRIORITY', 'VIP Priority'),
    )
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.ForeignKey('categories.Category', on_delete=models.CASCADE, related_name='menu_items')
    is_available = models.BooleanField(default=True)
    quantity = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="menu_items/") 
    vip_status = models.CharField(
        max_length=12,
        choices=VIP_STATUS_CHOICES,
        default='REGULAR',
        help_text="Automatically set based on category type (VIP/NORMAL)"
    )
    preparation_time = models.PositiveIntegerField(
        default=15,
        help_text="Average preparation time in minutes"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category__display_order', 'name']
        verbose_name = 'Menu Item'
        verbose_name_plural = 'Menu Items'
        indexes = [
            models.Index(fields=['is_available']),
            models.Index(fields=['vip_status']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_vip_status_display()})"

    @property
    def is_vip_item(self):
        """Returns True if this is a VIP item (either VIP_ONLY or VIP_PRIORITY)"""
        return self.vip_status in ['VIP_ONLY', 'VIP_PRIORITY']

    def decrease_quantity(self, amount):
        """Decreases the item quantity by the specified amount"""
        if self.quantity < amount:
            return False
            
        updated = MenuItem.objects.filter(
            pk=self.pk,
            quantity__gte=amount
        ).update(
            quantity=F('quantity') - amount
        )
        
        if updated:
            self.refresh_from_db()
            if self.quantity == 0:
                self.is_available = False
                self.save(update_fields=['is_available'])
            return True
        return False

    def increase_quantity(self, amount):
        """Increases the item quantity by the specified amount"""
        self.quantity = F('quantity') + amount
        self.save(update_fields=['quantity'])
        self.refresh_from_db()
        
        if not self.is_available and self.quantity > 0:
            self.is_available = True
            self.save(update_fields=['is_available'])

    def save(self, *args, **kwargs):
        """
        Automatically sets vip_status based on category type:
        - VIP category becomes VIP_ONLY
        - NORMAL category becomes REGULAR
        Also handles availability based on quantity
        """
        # Ensure we have the latest category data if this is an existing instance
        if self.pk:
            self.category.refresh_from_db()
        
        # Set VIP status based on category type
        if self.category.category_type == 'VIP':
            if not self.is_vip_item:  # Only change if not already a VIP item
                self.vip_status = 'VIP_ONLY'
        else:  # NORMAL category
            if self.is_vip_item:  # Only change if currently a VIP item
                self.vip_status = 'REGULAR'
        
        # Handle availability based on quantity
        if self.quantity == 0 and self.is_available:
            self.is_available = False
        elif self.quantity > 0 and not self.is_available:
            self.is_available = True
            
        super().save(*args, **kwargs)