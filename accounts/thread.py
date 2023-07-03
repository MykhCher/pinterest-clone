from django.conf import settings
from django.contrib.auth import get_user_model
from smtplib import SMTPException
from .otp import send_account_otp, send_verification_token

import threading
import logging


User = get_user_model()


class SendForgotPasswordEmail(threading.Thread):

    def __init__(self, email: str, user: User) -> None:
        self.user = user
        self.email = email
        self._otp = 0
        threading.Thread.__init__(self)

    def run(self) -> None:
        try:
            subject = "@noreply: Your one-time code to reset your password."
            self._otp = send_account_otp(self.email, self.user, subject)
        except SMTPException as e:
            logging.info("There is some error in sending a message. %s", e)

    def get_otp(self) -> int:
        return self._otp
    

class SendVerificationToken(threading.Thread):

    def __init__(self, email: str, user: User) -> None:
        self.user = user
        self.email = email
        threading.Thread.__init__(self)

    def run(self) -> None:
        try:
            subject = "@noreply: Verify your Pinterest account."
            send_verification_token(self.email, self.user, subject)
        except SMTPException as e:
            logging.info("There is some error in sending a message. %s", e)