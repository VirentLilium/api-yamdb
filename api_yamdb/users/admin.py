from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
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
    fieldsets = UserAdmin.fieldsets + (
        ('Extra Fields', {'fields': ('bio', 'role',)}),
    )
