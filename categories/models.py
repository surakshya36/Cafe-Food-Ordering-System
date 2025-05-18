from django.db import models

class Category(models.Model):
 
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    display_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    category_type = models.CharField(
        max_length=10, 
        default='NORMAL',
        help_text="VIP items are only available in VIP rooms"
    )

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['display_order', 'name']

    def __str__(self):
        return f"{self.get_category_type_display()} - {self.name}"