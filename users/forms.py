from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordResetForm, SetPasswordForm

from mailing.forms import MixinForms
from .models import ModelUser


class MixinValidPhoneNumber:
    """Миксин для проверки валидности номера телефона"""

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if phone_number and not phone_number.isdigit():
            raise forms.ValidationError("Номер телефона должен состоять только из цифр")
        return phone_number


class UserAuthenticationForm(MixinForms, AuthenticationForm):
    """Форма авторизации"""
    pass


class UserPasswordResetForm(MixinForms, PasswordResetForm):
    """Форма ввода E-mail для сброса пароля"""
    pass


class UserSetPasswordForm(MixinForms, SetPasswordForm):
    """Форма сброса пароля"""
    pass


class CustomUserCreationForm(MixinForms, UserCreationForm, MixinValidPhoneNumber):
    """Форма регистрации профиля"""

    phone_number = forms.CharField(max_length=15, required=False, label="Номер телефона")
    username = forms.CharField(max_length=100, required=True)

    class Meta:
        model = ModelUser
        fields = (
            "email",
            "username",
            "phone_number",
            "password1",
            "password2",
        )


class ProfileUserForm(MixinForms, forms.ModelForm, MixinValidPhoneNumber):
    """Форма профиля"""

    class Meta:
        model = ModelUser
        fields = ("last_name", "first_name", "username", "phone_number")
