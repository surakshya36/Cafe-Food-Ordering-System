from django.db import models
from django.conf import settings
from menuitems.models import MenuItem

class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'session_key')

    @classmethod
    def get_or_create_cart(cls, request):
        """Get or create cart for the current request"""
        if request.user.is_authenticated:
            # For logged-in users
            cart, created = cls.objects.get_or_create(user=request.user)
            
            # Merge session cart if exists
            if request.session.session_key:
                session_cart = cls.objects.filter(
                    session_key=request.session.session_key,
                    user__isnull=True
                ).first()
                if session_cart:
                    for item in session_cart.items.all():
                        item.cart = cart
                        item.save()
                    session_cart.delete()
        else:
            # For anonymous users
            if not request.session.session_key:
                request.session.create()
            cart, created = cls.objects.get_or_create(
                session_key=request.session.session_key,
                user=None
            )
        return cart

    @property
    def total_items(self):
        return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0

    @property
    def subtotal(self):
        return sum(item.subtotal for item in self.items.all())

    def merge_with(self, other_cart):
        """Merge another cart into this one"""
        for item in other_cart.items.all():
            existing = self.items.filter(menu_item=item.menu_item).first()
            if existing:
                existing.quantity += item.quantity
                existing.save()
            else:
                item.cart = self
                item.save()

    def __str__(self):
        return f"Cart #{self.id} ({self.user or 'anonymous'})"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        related_name='items',
        on_delete=models.CASCADE
    )
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)
    special_requests = models.TextField(blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    @property
    def subtotal(self):
        return self.menu_item.price * self.quantity

    def increase(self, amount=1):
        self.quantity += amount
        self.save()

    def decrease(self, amount=1):
        self.quantity = max(1, self.quantity - amount)
        self.save()

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name}"