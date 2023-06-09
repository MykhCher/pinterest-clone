from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from smtplib import SMTPException
from .models import CustomUser

import secrets
import logging


def send_account_otp(email: str, user: CustomUser, subject: str) -> int | None:
    """basic method, used to send an email with 4-digit one-time code."""

    # Generate code, message, configure the sender and recipient.
    otp = secrets.choice(range(1000, 10000))
    message = f"Hi {user.username},\n\nYour account one-time-password is {otp}.\
                \n This one-time code will expire in the next 10 minutes.\
                \n Kindly supply it to move forward in the pipeline.\n\n\nCheers"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]

    # Create thread-safe conditions, check for exceptions.
    try:
        send_mail(subject, message, email_from, recipient_list)
    except SMTPException as e:
        logging.info("There was some error in sending a message. %s", e)
        return

    return otp


def send_verification_token(email: str, user: CustomUser, subject: str) -> None:
    # Generate token.
    generator = PasswordResetTokenGenerator()
    token = generator.make_token(user)

    # Make message, configure recipient.
    message = render_to_string(
                template_name="acc_activate_email.html",
                context={
                    "username": user.username,
                    "domain": settings.DEFAULT_DOMAIN,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": token,
                }
            )
    recipient_list = [email]

    # Create thread-safe conditions, check for exceptions.
    try:
        send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)
    except SMTPException as e:
        logging.info(e)

    return None