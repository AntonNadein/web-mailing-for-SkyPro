from django.contrib.auth.models import AbstractUser
from django.db import models


class ModelUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
    ]

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "пользователя"
        verbose_name_plural = "Пользователи"
