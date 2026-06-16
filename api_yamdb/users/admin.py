"""Настройки административной панели для пользователей."""

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

User = get_user_model()


@admin.register(User)
class UserAdminConfig(UserAdmin):
    """Настройки отображения пользователей в административной панели."""

    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'bio',
        'role',
        'is_staff',
    )
    list_editable = (
        'role',
        'first_name',
        'last_name',
    )
    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
    list_filter = (
        'role',
        'is_staff',
        'is_active',
    )
    fieldsets = UserAdmin.fieldsets + (
        (
            'Extra Fields',
            {
                'fields': (
                    'bio',
                    'role',
                ),
            },
        ),
    )
