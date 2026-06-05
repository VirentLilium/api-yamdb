from django.urls import include, path
from rest_framework import routers

from api.views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                       ReviewViewSet, SignupAPIView, TitleViewSet,
                       TokenAPIView, UserViewSet)

api_version_prefix = 'v1'

v1_router = routers.DefaultRouter()

v1_router.register('categories', CategoryViewSet, basename='category')
v1_router.register('genres', GenreViewSet, basename='genre')
v1_router.register('titles', TitleViewSet, basename='title')
v1_router.register('users', UserViewSet, basename='user')
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='review'
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comment'
)

token_urlpatterns = [
    path('token/', TokenAPIView.as_view(), name='get_token'),
    path('signup/', SignupAPIView.as_view(), name='signup'),
]

urlpatterns = [
    path(f'{api_version_prefix}/auth/', include(token_urlpatterns)),
    path(f'{api_version_prefix}/', include(v1_router.urls)),
]
