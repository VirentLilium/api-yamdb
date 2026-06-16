"""Модель пользователя проекта YaMDb."""

from django.contrib.auth.models import AbstractUser
from django.db import models

from api.validators import username_validator
from api_yamdb.constants import (
    MAX_EMAIL_LENGTH,
    MAX_FIRST_NAME_LENGTH,
    MAX_LAST_NAME_LENGTH,
    MAX_USERNAME_LENGTH,
)


class User(AbstractUser):
    """Пользователь проекта."""

    class Role(models.TextChoices):
        """Роли пользователей."""

        USER = 'user', 'Пользователь'
        MODERATOR = 'moderator', 'Модератор'
        ADMIN = 'admin', 'Администратор'

    username = models.CharField(
        max_length=MAX_USERNAME_LENGTH,
        unique=True,
        validators=(username_validator,),
        verbose_name='username пользователя',
    )
    email = models.EmailField(
        max_length=MAX_EMAIL_LENGTH,
        unique=True,
        verbose_name='e-mail пользователя',
    )
    first_name = models.CharField(
        max_length=MAX_FIRST_NAME_LENGTH,
        blank=True,
        verbose_name='first name пользователя',
    )
    last_name = models.CharField(
        max_length=MAX_LAST_NAME_LENGTH,
        blank=True,
        verbose_name='last name пользователя',
    )
    bio = models.TextField(
        blank=True,
        verbose_name='Биография пользователя',
    )
    role = models.CharField(
        choices=Role.choices,
        max_length=max(len(role) for role, _ in Role.choices),
        default=Role.USER,
        verbose_name='Роль пользователя',
    )

    class Meta:
        """Настройки модели пользователя."""

        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self) -> str:
        """
        Возвращает строковое представление пользователя.

        :return: Username пользователя.
        """
        return f'{self.username}: {self.first_name} {self.last_name}'

    @property
    def is_admin(self) -> bool:
        """
        Проверяет, является ли пользователь администратором.

        :return: True, если пользователь администратор.
        """
        return (
            self.is_staff
            or self.role == self.Role.ADMIN
            or self.is_superuser
        )

    @property
    def is_moderator(self) -> bool:
        """
        Проверяет, является ли пользователь модератором.

        :return: True, если пользователь модератор.
        """
        return self.role == self.Role.MODERATOR
