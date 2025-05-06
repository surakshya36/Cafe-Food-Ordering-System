from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def create_default_admin(sender, **kwargs):
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@mycafe.local',
            password='MyCafe123@$$',
            role='admin'  # if your custom user model requires it
        )
        print("✅ Default admin user created.")
    else:
        print("ℹ️ Default admin user already exists.")
