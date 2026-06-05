from datetime import date

from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from api_yamdb.constants import MIN_REVIEW_RATING, MAX_REVIEW_RATING
from reviews.models import Category, Comment, Genre, Review, Title


class TitleForm(forms.ModelForm):
    """Форма для внесения произведения в БД через админ-зону."""
    class Meta:
        model = Title
        fields = '__all__'

    def clean_year(self):
        """
        Метод валидации года.

        Проверяет, что год выпуска произведения не больше текущего.

        Исключения:
            ValidationError
        """
        year = self.cleaned_data['year']
        if year > date.today().year:
            raise ValidationError('Нельзя установить год позже текущего!')
        return year


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    form = TitleForm
    list_display = ('id', 'name', 'year', 'category')
    list_filter = ('year', 'category')
    search_fields = ('name',)


class ReviewForm(forms.ModelForm):
    """Форма для внесения отзыва на произведение в БД через админ-зону."""
    class Meta:
        model = Review
        fields = '__all__'

    def clean_score(self):
        """
        Метод валидации рейтинга в отзыве.

        Проверяет, что рейтинг указан числом в диапазоне от 1 до 10.

        Исключения:
            ValidationError
        """
        score = self.cleaned_data['score']

        if not (MIN_REVIEW_RATING <= score <= MAX_REVIEW_RATING):
            raise ValidationError(
                f'Рейтинг должен быть в диапазоне от '
                f'{MIN_REVIEW_RATING} до {MAX_REVIEW_RATING}.'
            )
        return score


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    form = ReviewForm
    list_display = ('id', 'title', 'author', 'score', 'pub_date')
    list_filter = ('score', 'pub_date')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('name', 'slug')


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('name', 'slug')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'review', 'author', 'pub_date')
    search_fields = ('author__username', 'text')
    list_filter = ('pub_date',)
