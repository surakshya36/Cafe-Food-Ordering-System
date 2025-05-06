from django.db import models

class Room(models.Model):
    ROOM_TYPES = (
        ('VIP', 'VIP Room'),
        ('NORMAL', 'Normal Room'),
    )
    
    name = models.CharField(max_length=100)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPES)
    description = models.TextField(blank=True)
    capacity = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['room_type', 'name']
        
    def __str__(self):
        return f"{self.get_room_type_display()} - {self.name}"

class Table(models.Model):
    TABLE_STATUS = (
        ('AVAILABLE', 'Available'),
        ('OCCUPIED', 'Occupied'),
        ('RESERVED', 'Reserved'),
        ('MAINTENANCE', 'Maintenance'), 
    )
    
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='tables')
    table_number = models.CharField(max_length=10)
    seats = models.PositiveIntegerField()
    status = models.CharField(max_length=15, choices=TABLE_STATUS, default='AVAILABLE')
    x_position = models.FloatField(null=True, blank=True)
    y_position = models.FloatField(null=True, blank=True)
    current_order = models.OneToOneField(
        'orders.Order', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        related_name='active_table'
    )
    
    class Meta:
        ordering = ['room', 'table_number']
        unique_together = ['room', 'table_number']
        
    def __str__(self):
        return f"Table {self.table_number} ({self.room})"
    
    @property
    def active_payment(self):
        if self.current_order:
            try:
                from payments.models import Payment
                return Payment.objects.filter(order=self.current_order).first()
            except ImportError:
                return None
        return None