"""Валидаторы приложения reviews."""

from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_year(value: int) -> None:
    """
    Проверяет, что год выпуска произведения не больше текущего года.

    :param value: Проверяемый год.
    :return: None.
    :raises ValidationError: Если год больше текущего.
    """
    if value > timezone.now().year:
        raise ValidationError(
            'Год выпуска произведения не может быть больше текущего!'
        )
