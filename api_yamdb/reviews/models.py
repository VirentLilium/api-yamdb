"""Модели категорий, жанров, произведений, отзывов и комментариев."""

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from api_yamdb.constants import (
    DISPLAY_TEXT_LENGTH,
    MAX_NAME_LENGTH,
    MAX_REVIEW_RATING,
    MIN_REVIEW_RATING,
)
from reviews.validators import validate_year

User = get_user_model()


class CategoryGenreAbstractModel(models.Model):
    """Абстрактная модель для категорий и жанров."""

    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='Название',
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Slug',
    )

    class Meta:
        """Настройки абстрактной модели категорий и жанров."""

        abstract = True
        ordering = ('name',)

    def __str__(self) -> str:
        """
        Возвращает строковое представление объекта.

        :return: Название объекта.
        """
        return self.name[:DISPLAY_TEXT_LENGTH]


class ReviewCommentAbstractModel(models.Model):
    """Абстрактная модель для отзывов и комментариев."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор контента',
    )
    text = models.TextField(
        verbose_name='Текст контента',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации контента',
    )

    class Meta:
        """Настройки абстрактной модели отзывов и комментариев."""

        abstract = True
        ordering = ('-pub_date',)


class Category(CategoryGenreAbstractModel):
    """Категория произведения."""

    class Meta(CategoryGenreAbstractModel.Meta):
        """Настройки модели категории."""

        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(CategoryGenreAbstractModel):
    """Жанр произведения."""

    class Meta(CategoryGenreAbstractModel.Meta):
        """Настройки модели жанра."""

        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    """Произведение, к которому пользователи оставляют отзывы."""

    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='Название произведения',
    )
    year = models.SmallIntegerField(
        validators=(validate_year,),
        verbose_name='Год выпуска произведения',
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание произведения',
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр произведения',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория произведения',
    )

    class Meta:
        """Настройки модели произведения."""

        default_related_name = 'titles'
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('name',)

    def __str__(self) -> str:
        """
        Возвращает строковое представление произведения.

        :return: Название произведения.
        """
        return self.name[:DISPLAY_TEXT_LENGTH]


class Review(ReviewCommentAbstractModel):
    """Отзыв пользователя на произведение."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение',
    )
    score = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(MIN_REVIEW_RATING),
            MaxValueValidator(MAX_REVIEW_RATING),
        ],
        verbose_name=(
            f'Оценка произведения по шкале от {MIN_REVIEW_RATING} '
            f'до {MAX_REVIEW_RATING}'
        ),
    )

    class Meta(ReviewCommentAbstractModel.Meta):
        """Настройки модели отзыва."""

        default_related_name = 'reviews'
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'title'),
                name='unique_review',
            ),
        ]

    def __str__(self) -> str:
        """
        Возвращает строковое представление отзыва.

        :return: Произведение, автор и оценка.
        """
        return f'{self.title} - {self.author} ({self.score})'


class Comment(ReviewCommentAbstractModel):
    """Комментарий пользователя к отзыву."""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв',
    )

    class Meta(ReviewCommentAbstractModel.Meta):
        """Настройки модели комментария."""

        default_related_name = 'comments'
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self) -> str:
        """
        Возвращает строковое представление комментария.

        :return: Автор комментария и связанный отзыв.
        """
        return f'Комментарий от {self.author} к отзыву "{self.review}"'
