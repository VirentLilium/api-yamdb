"""Настройки административной панели для приложения reviews."""

from django.contrib import admin

from reviews.models import Category, Comment, Genre, Review, Title


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    """Настройки отображения произведений в административной панели."""

    list_display = (
        'id',
        'name',
        'year',
        'category',
    )
    search_fields = (
        'name',
    )
    list_filter = (
        'year',
        'category',
    )
    list_select_related = (
        'category',
    )
    empty_value_display = '-пусто-'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Настройки отображения отзывов в административной панели."""

    list_display = (
        'id',
        'title',
        'author',
        'score',
        'pub_date',
    )
    search_fields = (
        'title__name',
        'author__username',
    )
    list_filter = (
        'score',
        'pub_date',
    )
    list_select_related = (
        'title',
        'author',
    )
    empty_value_display = '-пусто-'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Настройки отображения категорий в административной панели."""

    list_display = (
        'id',
        'name',
        'slug',
    )
    search_fields = (
        'name',
        'slug',
    )
    prepopulated_fields = {
        'slug': ('name',),
    }
    empty_value_display = '-пусто-'


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """Настройки отображения жанров в административной панели."""

    list_display = (
        'id',
        'name',
        'slug',
    )
    search_fields = (
        'name',
        'slug',
    )
    prepopulated_fields = {
        'slug': ('name',),
    }
    empty_value_display = '-пусто-'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Настройки отображения комментариев в административной панели."""

    list_display = (
        'id',
        'review',
        'author',
        'pub_date',
    )
    search_fields = (
        'author__username',
        'text',
    )
    list_filter = (
        'pub_date',
    )
    list_select_related = (
        'review',
        'author',
    )
    empty_value_display = '-пусто-'
