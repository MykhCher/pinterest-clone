from django.conf import settings
from django.contrib.auth import get_user_model
from smtplib import SMTPException
from .otp import send_account_otp

import threading
import logging


User = get_user_model()


class SendForgotPasswordEmail(threading.Thread):

    def __init__(self, email: str, user: User) -> None:
        self.user = user
        self.email = email
        self._otp = 0
        threading.Thread.__init__(self)

    def run(self):
        try:
            subject = "@noreply: Your one-time code to reset your password."
            self._otp = send_account_otp(self.email, self.user, subject)
        except SMTPException as e:
            logging.info("There is some error in sending a message. %s", e)

    def get_otp(self):
        return self._otp