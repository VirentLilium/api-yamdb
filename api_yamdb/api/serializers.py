"""Сериализаторы API."""

from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from api.validators import username_validator
from api_yamdb.constants import (
    MAX_EMAIL_LENGTH,
    MAX_REVIEW_RATING,
    MAX_USERNAME_LENGTH,
    MIN_REVIEW_RATING,
)
from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class SignUpSerializer(serializers.Serializer):
    """Сериализатор регистрации пользователя."""

    username = serializers.CharField(
        max_length=MAX_USERNAME_LENGTH,
        required=True,
        validators=(username_validator,),
    )
    email = serializers.EmailField(
        max_length=MAX_EMAIL_LENGTH,
        required=True,
    )

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Проверяет уникальность связки username и email.

        Повторная регистрация разрешена только если username и email
        принадлежат одному и тому же пользователю.

        :param data: Данные регистрации.
        :return: Проверенные данные.
        :raises serializers.ValidationError: Если username или email заняты.
        """
        username = data['username']
        email = data['email']

        user_by_username = User.objects.filter(username=username).first()
        user_by_email = User.objects.filter(email=email).first()

        if user_by_username and user_by_username.email != email:
            raise serializers.ValidationError(
                'Пользователь с таким username уже существует'
            )

        if user_by_email and user_by_email.username != username:
            raise serializers.ValidationError(
                'Этот email не соответствует username'
            )

        return data

    def create(self, validated_data: dict[str, Any]) -> Any:
        """
        Создаёт или возвращает существующего пользователя.

        :param validated_data: Проверенные данные регистрации.
        :return: Пользователь.
        """
        user, _ = User.objects.get_or_create(**validated_data)
        return user


class TokenSerializer(serializers.Serializer):
    """Сериализатор получения JWT-токена."""

    username = serializers.CharField(
        max_length=MAX_USERNAME_LENGTH,
        required=True,
        validators=(username_validator,),
    )
    confirmation_code = serializers.CharField(
        required=True,
    )

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Проверяет код подтверждения пользователя.

        :param data: Данные для получения токена.
        :return: Проверенные данные.
        :raises serializers.ValidationError: Если код подтверждения неверен.
        """
        username = data['username']
        confirmation_code = data['confirmation_code']

        user = get_object_or_404(User, username=username)

        if not default_token_generator.check_token(user, confirmation_code):
            raise serializers.ValidationError('Неверный код подтверждения')

        self.user = user
        return data


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категории."""

    class Meta:
        """Настройки сериализатора категории."""

        model = Category
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор жанра."""

    class Meta:
        """Настройки сериализатора жанра."""

        model = Genre
        exclude = ('id',)


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор чтения произведений."""

    rating = serializers.IntegerField(read_only=True, default=None)
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        """Настройки сериализатора чтения произведений."""

        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category',
        )


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор создания и обновления произведений."""

    genre = serializers.SlugRelatedField(
        many=True,
        queryset=Genre.objects.all(),
        slug_field='slug',
        allow_empty=False,
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',
    )

    class Meta:
        """Настройки сериализатора записи произведений."""

        model = Title
        fields = (
            'id',
            'name',
            'year',
            'description',
            'genre',
            'category',
        )

    def to_representation(self, instance: Title) -> dict[str, Any]:
        """
        Возвращает представление произведения через read-сериализатор.

        :param instance: Объект произведения.
        :return: Данные произведения.
        """
        return TitleReadSerializer(instance).data


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор отзыва."""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
    )
    score = serializers.IntegerField(
        validators=[
            MinValueValidator(MIN_REVIEW_RATING),
            MaxValueValidator(MAX_REVIEW_RATING),
        ],
    )

    class Meta:
        """Настройки сериализатора отзыва."""

        model = Review
        fields = (
            'id',
            'text',
            'author',
            'score',
            'pub_date',
        )

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Проверяет возможность создания отзыва.

        Пользователь может оставить только один отзыв на одно произведение.

        :param data: Данные отзыва.
        :return: Проверенные данные.
        :raises serializers.ValidationError: Если отзыв уже существует.
        """
        request = self.context['request']
        view = self.context['view']

        if request.method == 'POST':
            title = view.get_title()
            user = request.user

            if Review.objects.filter(title=title, author=user).exists():
                raise serializers.ValidationError(
                    'Вы уже оставляли отзыв на это произведение!'
                )

        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментария."""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
    )

    class Meta:
        """Настройки сериализатора комментария."""

        model = Comment
        fields = (
            'id',
            'text',
            'author',
            'pub_date',
        )


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""

    class Meta:
        """Настройки сериализатора пользователя."""

        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )

    def validate_username(self, value: str) -> str:
        """
        Проверяет username пользователя.

        :param value: Проверяемый username.
        :return: Проверенный username.
        :raises ValidationError: Если username недопустим.
        """
        return username_validator(value)
