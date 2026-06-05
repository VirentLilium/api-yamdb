from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from api.filters import TitleFilter
from api.permissions import (IsAdmin, IsAdminOrReadOnly,
                             IsAdminModeratorAuthorOrReadOnly)
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, ReviewSerializer,
                             SignUpSerializer, TitleReadSerializer,
                             TitleWriteSerializer, TokenSerializer,
                             UserSerializer)
from reviews.models import Category, Genre, Review, Title

User = get_user_model()


class BaseAuthAPIView(APIView):
    """
    Базовое API-представление для аутентификационных эндпоинтов.

    Обрабатывает общий поток POST-запросов:
        - создание сериализатора
        - валидация входных данных
        - передача управления в handle()

    Наследники должны реализовать метод handle(),
    содержащий бизнес-логику конкретного эндпоинта.
    """

    serializer_class = None

    def post(self, request):
        """
        Обрабатывает POST-запрос:
            - валидирует входные данные через serializer
            - вызывает handle() при успешной валидации
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.handle(serializer)

    def handle(self, serializer):
        """
        Абстрактный метод обработки бизнес-логики.

        Исключения:
            NotImplementedError: если метод не переопределён в дочернем классе
        """
        raise NotImplementedError


class SignupAPIView(BaseAuthAPIView):
    """Создаёт пользователя и отправляет email с кодом подтверждения."""

    serializer_class = SignUpSerializer

    def handle(self, serializer):
        """
        Создаёт пользователя и отправляет confirmation_code на email.

        Возвращает:
            данные созданного пользователя
        """
        user = serializer.save()
        confirmation_code = default_token_generator.make_token(user)

        send_mail(
            subject='Код подтверждения',
            message=f'Confirmation code: {confirmation_code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=(user.email,),
            fail_silently=True)

        return Response(
            {"username": user.username, "email": user.email}
        )


class TokenAPIView(BaseAuthAPIView):
    """
    Эндпоинт получения JWT-токена.

    Пользователь отправляет:
        - username
        - confirmation_code

    Получает:
        - JWT token

    Token формируется после успешной валидации serializer.
    """

    serializer_class = TokenSerializer

    def handle(self, serializer):
        """Возвращает JWT-токен после успешной валидации."""
        token = str(serializer.validated_data['token'])
        return Response(
            {'token': token}
        )


class CategoryGenreMixinViewSet(mixins.ListModelMixin,
                                mixins.CreateModelMixin,
                                mixins.DestroyModelMixin,
                                viewsets.GenericViewSet):
    """
    Mixin для категорий и жанров.

    Обеспечивает:
        - пагинацию
        - доступ ()
        - поиск по имени name
        - обращение к объекту по slug
    """
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoryViewSet(CategoryGenreMixinViewSet):
    """
    ViewSet для модели Category.

    Позволяет:
        - получать список категорий (GET), все пользователи
        - добавлять новую категорию (POST), администратор
        - удалять категорию (DELETE), администратор
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreMixinViewSet):
    """
    ViewSet для модели Genre.

    Позволяет:
        - получать список жанров (GET), все пользователи
        - добавлять новый жанр (POST), администратор
        - удалять жанр (DELETE), администратор
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели Title.

    Позволяет:
        - получать список произведений (GET), все пользователи
        - получать отдельное произведение (GET), все пользователи
        - добавлять произведение (POST), администратор
        - частично обновлять информацию о произведении (PATCH), администратор
        - удалять произведение (DELETE), администратор

    Поддерживает фильтрацию.

    Вычисляет среднюю оценку произведения на основании отзывов.
    """
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    http_method_names = ('get', 'post', 'patch', 'delete',)
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели Review.

    Отзывы привязаны к конкретному произведению по title_id.

    Позволяет:
        - получать список отзывов к произведению (GET), все пользователи
        - получать отдельный отзыв (GET), все пользователи
        - добавлять отзыв (POST), аутентифицированный пользователь
        - частично обновлять отзыв (PATCH), автор, модератор или администратор
        - удалять отзыв (DELETE), автор, модератор или администратор
    """
    serializer_class = ReviewSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAdminModeratorAuthorOrReadOnly
    )
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs['title_id'])

    def get_queryset(self):
        title = self.get_title()
        return title.reviews.select_related('author')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели Comment.

    Комментарии привязаны к конкретным произведениям и отзывам по их id.

    Позволяет:
        - получать список комментариев (GET), все пользователи
        - получать отдельный комментарий (GET), все пользователи
        - добавлять комментарий (POST), аутентифицированный пользователь
        - частично обновлять комментарий (PATCH), автор, модератор или
        администратор
        - удалять комментарий (DELETE), автор, модератор или администратор
    """
    serializer_class = CommentSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAdminModeratorAuthorOrReadOnly
    )
    http_method_names = ('get', 'post', 'patch', 'delete',)

    def get_review(self):
        return get_object_or_404(
            Review,
            pk=self.kwargs['review_id'],
            title_id=self.kwargs['title_id'])

    def get_queryset(self):
        review = self.get_review()
        return review.comments.select_related('author')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели User.

    Доступ только для администратора:
        - получать список всех пользователей (GET)
        - получать отдельного пользователя (GET)
        - добавлять пользователя (POST)
        - частично обновлять данные пользователя (PATCH)
        - удалять пользователя (DELETE)
        - поиск по username

    Доступ для любого авторизованного пользователя:
        - получение и изменение данных своей учетной записи по 'me'
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = (IsAdmin,)
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    http_method_names = ('get', 'post', 'patch', 'delete',)

    @action(methods=['get', 'patch'], detail=False, url_path='me',
            permission_classes=(permissions.IsAuthenticated,)
            )
    def me(self, request):
        user = request.user
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                user,
                data=request.data,
                partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(role=user.role)
        else:
            serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
