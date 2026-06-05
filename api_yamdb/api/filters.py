from django_filters.rest_framework import CharFilter, FilterSet

from reviews.models import Title


class TitleFilter(FilterSet):
    """
    Класс для фильтрации произведений.

    Фильтрация:
        - slug категории
        - slug жанра
        - название произведения
        - год выпуска произведения
    """
    name = CharFilter(
        field_name='name',
        lookup_expr='contains',
    )
    category = CharFilter(
        field_name='category__slug',
        lookup_expr='contains')
    genre = CharFilter(
        field_name='genre__slug',
        lookup_expr='contains')

    class Meta:
        model = Title
        fields = ('genre', 'category', 'name', 'year')
