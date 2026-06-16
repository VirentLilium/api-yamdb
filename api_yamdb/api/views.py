"""View-классы и ViewSet-классы API."""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg, IntegerField, QuerySet
from django.db.models.functions import Cast
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from api.filters import TitleFilter
from api.permissions import (
    IsAdmin,
    IsAdminModeratorAuthorOrReadOnly,
    IsAdminOrReadOnly,
)
from api.serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    SignUpSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    TokenSerializer,
    UserSerializer,
)
from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class BaseAuthAPIView(APIView):
    """Базовое API-представление для аутентификационных эндпоинтов."""

    serializer_class: type[BaseSerializer] | None = None

    def post(self, request: Request) -> Response:
        """
        Обрабатывает POST-запрос.

        Валидирует входные данные через serializer_class и передаёт
        обработку в метод handle.

        :param request: Объект HTTP-запроса.
        :return: HTTP-ответ.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.handle(serializer)

    def handle(self, serializer: BaseSerializer) -> Response:
        """
        Обрабатывает бизнес-логику эндпоинта.

        Метод должен быть переопределён в дочернем классе.

        :param serializer: Валидный сериализатор.
        :return: HTTP-ответ.
        :raises NotImplementedError: Если метод не переопределён.
        """
        raise NotImplementedError


class SignupAPIView(BaseAuthAPIView):
    """API-представление регистрации пользователя."""

    serializer_class = SignUpSerializer

    def handle(self, serializer: BaseSerializer) -> Response:
        """
        Создаёт пользователя и отправляет код подтверждения на email.

        :param serializer: Валидный сериализатор регистрации.
        :return: HTTP-ответ с username и email пользователя.
        """
        user = serializer.save()
        confirmation_code = default_token_generator.make_token(user)

        send_mail(
            subject='Код подтверждения',
            message=f'Confirmation code: {confirmation_code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=(user.email,),
            fail_silently=True,
        )

        return Response(
            {
                'username': user.username,
                'email': user.email,
            },
        )


class TokenAPIView(BaseAuthAPIView):
    """API-представление получения JWT-токена."""

    serializer_class = TokenSerializer

    def handle(self, serializer: BaseSerializer) -> Response:
        """
        Возвращает JWT-токен после успешной валидации.

        :param serializer: Валидный сериализатор получения токена.
        :return: HTTP-ответ с JWT-токеном.
        """
        token = str(AccessToken.for_user(serializer.user))

        return Response({'token': token})


class CategoryGenreMixinViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Базовый ViewSet для категорий и жанров."""

    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoryViewSet(CategoryGenreMixinViewSet):
    """ViewSet для категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreMixinViewSet):
    """ViewSet для жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """ViewSet для произведений."""

    queryset = Title.objects.annotate(
        rating=Cast(
            Avg('reviews__score'),
            IntegerField(),
        ),
    ).order_by('rating')

    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self) -> type[BaseSerializer]:
        """
        Возвращает сериализатор в зависимости от действия.

        Для чтения используется TitleReadSerializer.
        Для записи используется TitleWriteSerializer.

        :return: Класс сериализатора.
        """
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для отзывов к произведениям."""

    serializer_class = ReviewSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAdminModeratorAuthorOrReadOnly,
    )
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_title(self) -> Title:
        """
        Возвращает произведение из URL.

        :return: Объект произведения.
        :raises Http404: Если произведение не найдено.
        """
        return get_object_or_404(Title, pk=self.kwargs['title_id'])

    def get_queryset(self) -> QuerySet[Review]:
        """
        Возвращает отзывы текущего произведения.

        :return: QuerySet отзывов.
        """
        title = self.get_title()
        return title.reviews.select_related('author', 'title')

    def perform_create(self, serializer: BaseSerializer) -> None:
        """
        Сохраняет новый отзыв.

        Автором становится текущий пользователь,
        произведение берётся из URL.

        :param serializer: Сериализатор с валидированными данными.
        :return: None.
        """
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для комментариев к отзывам."""

    serializer_class = CommentSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAdminModeratorAuthorOrReadOnly,
    )
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_review(self) -> Review:
        """
        Возвращает отзыв из URL.

        :return: Объект отзыва.
        :raises Http404: Если отзыв не найден.
        """
        return get_object_or_404(
            Review,
            pk=self.kwargs['review_id'],
            title_id=self.kwargs['title_id'],
        )

    def get_queryset(self) -> QuerySet[Comment]:
        """
        Возвращает комментарии текущего отзыва.

        :return: QuerySet комментариев.
        """
        review = self.get_review()
        return review.comments.select_related('author', 'review')

    def perform_create(self, serializer: BaseSerializer) -> None:
        """
        Сохраняет новый комментарий.

        Автором становится текущий пользователь,
        отзыв берётся из URL.

        :param serializer: Сериализатор с валидированными данными.
        :return: None.
        """
        serializer.save(author=self.request.user, review=self.get_review())


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для пользователей."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = (IsAdmin,)
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    http_method_names = ('get', 'post', 'patch', 'delete')

    @action(
        methods=['get', 'patch'],
        detail=False,
        url_path='me',
        permission_classes=(permissions.IsAuthenticated,),
    )
    def me(self, request: Request) -> Response:
        """
        Возвращает или обновляет данные текущего пользователя.

        При PATCH-запросе роль пользователя сохраняется неизменной.

        :param request: Объект HTTP-запроса.
        :return: HTTP-ответ с данными пользователя.
        """
        user = request.user

        if request.method == 'PATCH':
            serializer = self.get_serializer(
                user,
                data=request.data,
                partial=True,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=user.role)
        else:
            serializer = self.get_serializer(user)

        return Response(serializer.data, status=status.HTTP_200_OK)
