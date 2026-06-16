"""URL-маршруты API."""

from django.urls import include, path
from rest_framework import routers

from api.views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    SignupAPIView,
    TitleViewSet,
    TokenAPIView,
    UserViewSet,
)

API_VERSION_PREFIX = 'v1'

v1_router = routers.DefaultRouter()

v1_router.register('categories', CategoryViewSet, basename='category')
v1_router.register('genres', GenreViewSet, basename='genre')
v1_router.register('titles', TitleViewSet, basename='title')
v1_router.register('users', UserViewSet, basename='user')
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='review',
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comment',
)

auth_urlpatterns = [
    path('token/', TokenAPIView.as_view(), name='get_token'),
    path('signup/', SignupAPIView.as_view(), name='signup'),
]

urlpatterns = [
    path(f'{API_VERSION_PREFIX}/auth/', include(auth_urlpatterns)),
    path(f'{API_VERSION_PREFIX}/', include(v1_router.urls)),
]
