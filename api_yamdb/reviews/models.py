from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from api_yamdb.constants import (MIN_REVIEW_RATING, MAX_REVIEW_RATING,
                                 DISPLAY_TEXT_LENGTH)

User = get_user_model()


class CategoryGenreAbstractModel(models.Model):
    """
    Абстрактная модель для моделей категорий и жанров.

    Атрибуты:
        name (str): Название.
        slug (slug): Слаг.
    """
    name = models.CharField(
        max_length=256,
        verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Slug'
    )

    class Meta:
        abstract = True


class ReviewCommentAbstractModel(models.Model):
    """
    Абстрактная модель для моделей отзывов и комментариев.

    Атрибуты:
        text (str): Текст контента.
        author (User): Автор контента.
        pub_date (datetime): Дата публикации контента.
    """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор контента'
    )
    text = models.TextField(
        verbose_name='Текст контента'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации контента'
    )

    class Meta:
        abstract = True


class Category(CategoryGenreAbstractModel):
    """
    Модель категорий произведений.

    Атрибуты:
        name (str): Название категории.
        slug (slug): Слаг категории.
    """
    class Meta(CategoryGenreAbstractModel.Meta):
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name[:DISPLAY_TEXT_LENGTH]


class Genre(CategoryGenreAbstractModel):
    """
    Модель жанров произведений.

    Атрибуты:
        name (str): Название жанра.
        slug (slug): Слаг жанра.
    """
    class Meta(CategoryGenreAbstractModel.Meta):
        verbose_name = 'genre'
        verbose_name_plural = 'genres'

    def __str__(self):
        return self.name[:DISPLAY_TEXT_LENGTH]


class Title(models.Model):
    """
    Модель произведения.

    Атрибуты:
        name (str): Название произведения.
        year (int): Год выпуска произведения.
        description (str | None): Описание произведения, опционально.
        genre (Genre): Жанр произведения.
        category (Category): Категория произведения.
    """
    name = models.CharField(
        max_length=256,
        verbose_name='Название произведения'
    )
    year = models.PositiveIntegerField(
        verbose_name='Год выпуска произведения'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание произведения'
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр произведения'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория произведения'
    )

    class Meta:
        default_related_name = 'titles'
        verbose_name = 'title'
        verbose_name_plural = 'titles'
        ordering = ('name',)

    def __str__(self):
        return self.name[:DISPLAY_TEXT_LENGTH]


class Review(ReviewCommentAbstractModel):
    """
    Модель отзывов на произведения.

    Атрибуты:
        text (str): Текст отзыва.
        author (User): Пользователь, написавший отзыв.
        title (Title): Произведение, с которым связан отзыв.
        score (int): Оценка произведения по шкале от 1 до 10.
        pub_date (datetime): Дата публикации отзыва.
    """
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение',
    )
    score = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(MIN_REVIEW_RATING),
            MaxValueValidator(MAX_REVIEW_RATING)
        ],
        verbose_name='Оценка произведения по шкале от 1 до 10'
    )

    class Meta(ReviewCommentAbstractModel.Meta):
        default_related_name = 'reviews'
        verbose_name = 'review'
        verbose_name_plural = 'reviews'
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'title'),
                name='unique_review'
            )
        ]

    def __str__(self):
        return f'{self.title} - {self.author} ({self.score})'


class Comment(ReviewCommentAbstractModel):
    """
    Модель комментариев к отзывам на произведения.

    Атрибуты:
        text (str): Текст комментария.
        author (User): Пользователь, написавший комментарий.
        review (Review): Отзыв, с которым связан комментарий.
        pub_date (datetime): Дата публикации комментария.
    """
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Комментарий',
    )

    class Meta(ReviewCommentAbstractModel.Meta):
        default_related_name = 'comments'
        verbose_name = 'comment'
        verbose_name_plural = 'comments'

    def __str__(self):
        return f'Комментарий от {self.author} к отзыву "{self.review}"'
