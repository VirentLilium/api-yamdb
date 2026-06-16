"""Фильтры для API приложения."""

from django_filters.rest_framework import CharFilter, FilterSet

from reviews.models import Title


class TitleFilter(FilterSet):
    """Фильтр произведений по названию, категории, жанру и году."""

    name = CharFilter(
        field_name='name',
        lookup_expr='contains',
    )
    category = CharFilter(
        field_name='category__slug',
        lookup_expr='contains',
    )
    genre = CharFilter(
        field_name='genre__slug',
        lookup_expr='contains',
    )

    class Meta:
        """Настройки фильтра произведений."""

        model = Title
        fields = ('genre', 'category', 'name', 'year')
