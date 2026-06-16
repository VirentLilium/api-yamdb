"""Конфигурация приложения reviews."""

from django.apps import AppConfig


class ReviewsConfig(AppConfig):
    """Конфигурация приложения reviews."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reviews'
    verbose_name = 'Отзывы пользователей'
