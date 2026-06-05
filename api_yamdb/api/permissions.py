from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    """
    Проверка на права администратора.

    Доступ выдается только аутентифицированному пользователю с ролью admin.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsAdminOrReadOnly(BasePermission):
    """
    Проверка на права администратора для POST-запросов на создание контента.

    Анонимные пользователи могут только читать контент.
    """
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or (
            request.user.is_authenticated and request.user.is_admin
        )


class IsAdminModeratorAuthorOrReadOnly(BasePermission):
    """
    Контроль PATCH и DELETE запросов к контенту.

    Разрешает изменение и удаление объекта только администратору, модератору
    или автору контента.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
            or request.user.is_moderator
            or request.user.is_admin
        )
