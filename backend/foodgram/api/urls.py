from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    IngredientViewSet,
    TagViewSet,
    RecipeViewSet,
    UserViewSet,
)

router_ver1 = DefaultRouter()
router_ver1.register(r'ingredients', IngredientViewSet, basename='ingredients')
router_ver1.register(r'tags', TagViewSet, basename='tags')
router_ver1.register(r'recipes', RecipeViewSet, basename='recipes ')
router_ver1.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router_ver1.urls)),
    path('auth/', include('djoser.urls')),
]
