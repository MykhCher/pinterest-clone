from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField, SetPasswordForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    username = UsernameField(
        max_length=64,
        label="Username",
        required=True,
        widget=forms.TextInput(
            attrs={
                "autocomplete": "username",
                'class': 'form-control rounded-pill', 
                'placeholder': 'Username',
            }
        ),
        help_text="Enter your username. Use UTF-8 symbols and digits(0-9)."
    )
    email = forms.EmailField(
        label="E-mail",
        required=True,
        widget=forms.EmailInput(
            attrs={
                "autocomplete": "email",
                'class': 'form-control rounded-pill', 
                'placeholder': 'Email',
            }
        )
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                'class': 'form-control rounded-pill', 
                'placeholder': 'Password',
            }
        ),
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                'class': 'form-control rounded-pill', 
                'placeholder': 'Confirm password',
            }
        ),
    )
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.clean_username()
        user.email = self.cleaned_data.get("email")
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
    
class UserLoginForm(AuthenticationForm):
    username = UsernameField(
        widget=forms.TextInput(
            attrs={'class': 'form-control rounded-pill', 'placeholder': 'Username'}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control rounded-pill', 'placeholder': 'Password'}
        )
    )


class CustomPasswordResetForm(SetPasswordForm):

    new_password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={ 
                'class': 'form-control rounded-pill', 
                'placeholder': 'Password',
            }
        ),
    )
    new_password2 = forms.CharField(
        label="Password confirmation",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control rounded-pill', 
                'placeholder': 'Confirm password',
            }
        ),
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user
    