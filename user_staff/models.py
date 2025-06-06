
from django.db import models
from orders.models import Order
from payments.models import Payment
from feedback.models import Feedback
from users.models import User

  # adjust import path if needed

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('order', 'Order'),
        ('order_Status', 'order_Status'),
        ('payment', 'Payment'),
        ('feedback', 'Feedback'),
        ('user_registration', 'User Registration'),
    ]
    metadata = models.JSONField(default=dict, blank=True)
    message = models.TextField()
    type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES, default='order')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    # Link to Order (if applicable)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')

    # Link to session-based anonymous user (if applicable)
    session_key = models.CharField(max_length=40, null=True, blank=True)

    # Link to Payment (if applicable)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
      
    # New optional links
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='registration_notifications')
    feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE, null=True, blank=True, related_name='feedback_notifications')

    def __str__(self):
        return f"{self.type.capitalize()} - {self.message[:30]}"

    @classmethod
    def create_order_status_notification(cls, order, message, session_key=None):
        """Helper method to create order status notifications"""
        return cls.objects.create(
            type='order_Status',
            message=message,
            order=order,
            session_key=session_key,
            metadata={
                'order_id': order.id,
                'status': order.status
            }
        )