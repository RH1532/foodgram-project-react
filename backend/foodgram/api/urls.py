from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet,
    FollowVievSet,
    IngredientViewSet,
    TagViewSet,
    RecipeViewSet,
)

router_ver1 = DefaultRouter()
router_ver1.register(r'users', UserViewSet, basename='users')
router_ver1.register(r'ingredients', IngredientViewSet, basename='ingredients')
router_ver1.register(r'tags', TagViewSet, basename='tags')
router_ver1.register(r'recipes', RecipeViewSet, basename='recipes ')

urlpatterns = [
    path('', include(router_ver1.urls)),
    path(r'auth/', include('djoser.urls.authtoken'))
]
