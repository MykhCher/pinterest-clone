from django.db.models.signals import post_save 
from django.dispatch import receiver
from .models import CustomUser, Profile


@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance: CustomUser, created: bool, **kwargs) -> None:
    """Creating profile instance, linked to saved User."""
    if created:
        Profile.objects.create(user=instance)

# @receiver(post_save, sender=CustomUser)
# def send_confirmation_email(sender, instance: CustomUser, created: bool, **kwargs) -> None:
#     
#   implement some logic for confirmation email sending signal.
