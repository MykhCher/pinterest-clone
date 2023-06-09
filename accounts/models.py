from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from .managers import CustomUserManager

SEX_CHOICES = [
    ('m', 'Male'),
    ('f', 'Female'),
    ('o', 'Other'),
]

class CustomUser(AbstractUser):

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        verbose_name="username",
        max_length=64,
        unique=True,
        help_text= "Required. 64 characters or fewer. Letters, digits and @/./+/-/_ only."
        ,
        validators=[username_validator],
        error_messages={
            "unique": "A user with that username already exists.",
        },
    )
    email = models.EmailField(
        "email", 
        unique=True, 
        blank=True
    )
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    def __str__(self) -> str:
        return self.username

    def has_perm(self, perm, obj=None) -> bool:
        return True

    def has_module_perms(self, app_label) -> bool:
        return True


class Profile(models.Model):

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField(
        verbose_name="first_name",
        max_length=64,
    )
    last_name = models.CharField(
        verbose_name="last_name",
        max_length=64,
    )
    description = models.TextField(verbose_name="description", blank=True)
    profile_status = models.CharField(verbose_name="profile_status", max_length=150, blank=True)
    photo = models.ImageField(default='profiles/default.png', upload_to='profiles')
    sex = models.CharField(choices=SEX_CHOICES, default='o')

    def __str__(self) -> str:
        return f"{self.user.username} profile"
    

class ForgotPassword(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="forgot_pass")
    forget_password_otp = models.CharField(max_length=5, null=True, blank=True)
    is_user_password_updated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username
    
    
class Follow(models.Model):
    follower = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='followers')
    following = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='following')

    objects = models.Manager()

    def __str__(self):
        return f'{self.follower} is following {self.following}'