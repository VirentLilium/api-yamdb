from django.contrib.auth.models import AbstractUser
from django.db import models

from api.validators import username_validator
from api_yamdb.constants import MAX_EMAIL_LENGTH, MAX_USERNAME_LENGTH


class CustomUser(AbstractUser):
    """
    Кастомная модель пользователя.

    Атрибуты:
        username (str): Имя пользователя.
        email (EmailField): e-mail пользователя.
        first_name (str | None): first_name пользователя.
        last_name (str | None): last_name пользователя.
        bio (str | None): Биография пользователя.
        role (Role): Роль пользователя в системе.
    """
    class Role(models.TextChoices):
        USER = 'user', 'Пользователь'
        MODERATOR = 'moderator', 'Модератор'
        ADMIN = 'admin', 'Администратор'

    username = models.CharField(
        max_length=MAX_USERNAME_LENGTH,
        unique=True,
        validators=(username_validator,),
        verbose_name='username пользователя'
    )
    email = models.EmailField(
        max_length=MAX_EMAIL_LENGTH,
        unique=True,
        verbose_name='e-mail пользователя'
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='first name пользователя'
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='last name пользователя'
    )
    bio = models.TextField(
        blank=True,
        verbose_name='Биография пользователя'
    )
    role = models.CharField(
        choices=Role.choices,
        max_length=100,
        default=Role.USER,
        verbose_name='Роль пользователя'
    )

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    @property
    def is_admin(self):
        return (
            self.is_staff
            or self.role == self.Role.ADMIN
            or self.is_superuser
        )

    @property
    def is_moderator(self):
        return self.role == self.Role.MODERATOR

    def __str__(self):
        return f'{self.username}: {self.first_name} {self.last_name}'
