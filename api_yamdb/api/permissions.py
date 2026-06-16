"""Права доступа для API."""

from typing import Any

from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.request import Request
from rest_framework.views import APIView


class IsAdmin(BasePermission):
    """Разрешает доступ только администраторам."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Проверяет, является ли пользователь администратором.

        :param request: Объект HTTP-запроса.
        :param view: View, для которого проверяются права.
        :return: True, если пользователь аутентифицирован и является админом.
        """
        return request.user.is_authenticated and request.user.is_admin


class IsAdminOrReadOnly(BasePermission):
    """Разрешает чтение всем, а изменение только администраторам."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Проверяет права пользователя на действие.

        Безопасные методы доступны всем пользователям.
        Изменение данных доступно только администраторам.

        :param request: Объект HTTP-запроса.
        :param view: View, для которого проверяются права.
        :return: True, если доступ разрешён.
        """
        return request.method in SAFE_METHODS or (
            request.user.is_authenticated and request.user.is_admin
        )


class IsAdminModeratorAuthorOrReadOnly(BasePermission):
    """Разрешает изменение объекта админу, модератору или автору."""

    def has_object_permission(
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ) -> bool:
        """
        Проверяет права пользователя на конкретный объект.

        Безопасные методы доступны всем пользователям.
        Изменение и удаление доступны администратору, модератору
        или автору объекта.

        :param request: Объект HTTP-запроса.
        :param view: View, для которого проверяются права.
        :param obj: Объект, для которого проверяется доступ.
        :return: True, если доступ разрешён.
        """
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
            or request.user.is_moderator
            or request.user.is_admin
        )
