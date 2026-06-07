from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_year(value):
    """
    Валидатор для поля year объектов модели Title.

    Год выпуска произведения (year) не может быть больше текущего.

    Исключения:
        ValidationError
    """
    if value > timezone.now().year:
        raise ValidationError(
            'Год выпуска произведения не может быть больше текущего!'
        )
