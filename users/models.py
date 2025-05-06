from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field is required")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('staff', 'Staff')
    ]
    
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    # Remove unused default fields
    first_name = None
    last_name = None

    # Added fields
    full_name = models.CharField(max_length=100, verbose_name='Full Name', help_text='Enter full name')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='staff')

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    # def save(self, *args, **kwargs):
    #     if not self.username and self.role == 'staff':
    #         # Generate a username like 'staff001'
    #         last_user = User.objects.filter(role='staff').order_by('-id').first()
    #         last_id = last_user.id if last_user else 0
    #         self.username = f"staff{last_id + 1:03d}"
    #     super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.role})"
