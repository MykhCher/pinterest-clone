from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, Profile, ForgotPassword
from .thread import SendForgotPasswordEmail, SendVerificationToken


@receiver(post_save, sender=CustomUser)
def user_deactivate(sender, instance: CustomUser, created: bool, **kwargs) -> None:
    """Set `CustomeUser.is_active` attribute `False`, until user 
    account wouldn't be confirmed via email.
    """
    if created:
        instance.is_active = False
        instance.save()


@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance: CustomUser, created: bool, **kwargs) -> None:
    """Creating profile instance, linked to saved User."""
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=CustomUser)
def send_confirmation_email(sender, instance: CustomUser, created: bool, **kwargs) -> None:
    """Send confirmation link to an email adress, provided by user."""
    try:
        if created:
            # Create and join new thread.
            new_thread = SendVerificationToken(instance.email, instance)
            new_thread.start()
            new_thread.join()

    except SystemError as e:
        print(e)


@receiver(post_save, sender=ForgotPassword)
def send_email_otp(sender, instance: ForgotPassword, created: bool, **kwagrs) -> ForgotPassword:
    """Send a 4-digit code to reset previous password."""
    try:
        if created:
            # Create new thread, start and join it.
            new_thread = SendForgotPasswordEmail(email=instance.user.email, user=instance.user)
            new_thread.start()
            new_thread.join()

            # Update user otp, write it to database.
            instance.forget_password_otp = new_thread.get_otp()
            instance.save()
            return instance
        
    except SystemError as e:
        print(e)