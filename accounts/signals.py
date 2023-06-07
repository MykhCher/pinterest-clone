from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.sites.models import Site
from django.core.mail import EmailMessage
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .models import CustomUser, Profile, ForgotPassword
from .thread import SendForgotPasswordEmail


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
    print(f"Caught 'post_save' singal. Created attribute is {created}.")
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=CustomUser)
def send_confirmation_email(sender, instance: CustomUser, created: bool, **kwargs) -> None:
    """Send confirmation link to an email adress, provided by user."""
    if created:
        generator = PasswordResetTokenGenerator()
        token = generator.make_token(instance)

        # Building email from existing template
        message = EmailMessage(
            subject="Activate your account!",
            body=render_to_string(
                template_name="acc_activate_email.html",
                context={
                    "username": instance.username,
                    "domain": settings.DEFAULT_DOMAIN,
                    "uid": urlsafe_base64_encode(force_bytes(instance.pk)),
                    "token": token,
                }
            ),
            to=instance.email,
        )

        message.send()


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