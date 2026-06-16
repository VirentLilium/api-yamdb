"""Валидаторы приложения API."""

import re

from django.core.exceptions import ValidationError

from api_yamdb.constants import FORBIDDEN_NAME, USERNAME_PATTERN


def username_validator(username: str) -> str:
    """
    Проверяет корректность username.

    Username не должен быть равен запрещённому имени и должен содержать
    только разрешённые символы.

    :param username: Проверяемое имя пользователя.
    :return: Проверенный username.
    :raises ValidationError: Если username недопустим.
    """
    if username == FORBIDDEN_NAME:
        raise ValidationError(
            f'username {FORBIDDEN_NAME} использовать нельзя'
        )

    if not re.fullmatch(USERNAME_PATTERN, username):
        raise ValidationError(
            'Неподдерживаемые символы в username'
        )

    return username
