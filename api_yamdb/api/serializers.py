from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from api.validators import username_validator
from api_yamdb.constants import (MAX_EMAIL_LENGTH, MAX_REVIEW_RATING,
                                 MAX_USERNAME_LENGTH, MIN_REVIEW_RATING)
from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class SignUpSerializer(serializers.Serializer):
    """
    Сериализатор для процесса регистрации.

    Обеспечивает:
        - валидацию username и email
        - создание нового пользователя

    Исключения:
        ValidationError: если введены занятые username и email
    """

    username = serializers.CharField(
        max_length=MAX_USERNAME_LENGTH,
        required=True,
        validators=(username_validator,)
    )
    email = serializers.EmailField(max_length=MAX_EMAIL_LENGTH, required=True)

    def validate(self, data):
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

    def create(self, validated_data):
        user, _ = User.objects.get_or_create(**validated_data)
        return user


class TokenSerializer(serializers.Serializer):
    """
    Сериализатор для получения токена.

    Обеспечивает:
        - валидацию username и confirmation_code

    Исключения:
        ValidationError: если код подтверждения неверен
    """

    username = serializers.CharField(
        max_length=MAX_USERNAME_LENGTH,
        required=True,
        validators=(username_validator,)
    )
    confirmation_code = serializers.CharField(required=True,)

    def validate(self, data):
        username = data['username']
        confirmation_code = data['confirmation_code']

        user = get_object_or_404(User, username=username)

        if not default_token_generator.check_token(user, confirmation_code):
            raise serializers.ValidationError('Неверный код подтверждения')

        self.user = user
        return data


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Category.

    Поддерживает:
        - получение списка категорий
        - добавление категории
        - удаление категории
    """

    class Meta:
        model = Category
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Genre.

    Поддерживает:
        - получение списка жанров
        - добавление жанра
        - удаление жанра
    """

    class Meta:
        model = Genre
        exclude = ('id',)


class TitleReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для чтения произведений.

    Поддерживает:
        - получение списка произведений (GET)
        - получение одного произведения (GET)
        - валидацию года выпуска произведения
    """

    rating = serializers.IntegerField(read_only=True, default=None)
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'description', 'genre',
                  'category')


class TitleWriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для записи в модель Title.

    Поддерживает:
        - создание произведения (POST)
        - частичное обновление и удаление произведения (PATCH, DELETE)
        - репрезентует ответ через TitleReadSerializer

    Исключения:
        ValidationError: нельзя добавлять произведение из будущего
    """

    genre = serializers.SlugRelatedField(
        many=True,
        queryset=Genre.objects.all(),
        slug_field='slug',
        allow_empty=False)
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug')

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')

    def to_representation(self, instance):
        return TitleReadSerializer(instance).data


class ReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Review.

    Поддерживает:
        - получение списка отзывов к произведению (GET)
        - получение одного отзыва (GET)
        - создание отзыва (POST)
        - частичное обновление и удаление отзыва (PATCH, DELETE)
        - валидацию рейтинга

    Исключения:
        ValidationError: на одно произведение можно оставить только один отзыв
    """

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    score = serializers.IntegerField(
        validators=[
            MinValueValidator(MIN_REVIEW_RATING),
            MaxValueValidator(MAX_REVIEW_RATING),
        ],
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
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
    """
    Сериализатор для модели Comment.

    Поддерживает:
        - получение списка комментариев к отзыву (GET)
        - получение одного комментария (GET)
        - создание комментария (POST)
        - частичное обновление и удаление комментария (PATCH, DELETE)
    """

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для пользователя User.

    Поддерживает:
        - получение списка всех пользователей (GET)
        - получение отдельного пользователя (GET)
        - добавление пользователя (POST)
        - частичное обновление данных пользователя (PATCH)
        - удаление пользователя (DELETE)
    """

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio',
                  'role')

    def validate_username(self, value):
        return username_validator(value)
