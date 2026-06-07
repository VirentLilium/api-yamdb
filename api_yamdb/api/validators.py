import re

from django.core.exceptions import ValidationError

from api_yamdb.constants import FORBIDDEN_NAME, USERNAME_PATTERN


def username_validator(username):
    """
    Валидатор для поля username объектов класса User.

    Проверяет, что username содержит только разрешенные символы.

    Исключения:
        ValidationError
    """
    if username == FORBIDDEN_NAME:
        raise ValidationError(
            f'username {FORBIDDEN_NAME} использовать нельзя'
        )

    pattern = USERNAME_PATTERN

    if not re.fullmatch(pattern, username):
        raise ValidationError(
            'Неподдерживаемые символы в username'
        )

    return username
