import re

from rest_framework import serializers


def username_validator(username):
    """
    Валидатор для поля username объектов класса User.

    Проверяет, что username содержит только разрешенные символы.

    username не может быть равен 'me'.

    Исключения:
        ValidationError
    """
    if username.lower() == 'me':
        raise serializers.ValidationError(
            'username "me" использовать нельзя'
        )

    pattern = r'^[\w.@+-]+\Z'

    if not re.fullmatch(pattern, username):
        raise serializers.ValidationError(
            'Неподдерживаемые символы в username'
        )

    return username
