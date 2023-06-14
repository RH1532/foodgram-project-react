from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    IngredientViewSet,
    TagViewSet,
    RecipeViewSet
)

router_ver1 = DefaultRouter()
router_ver1.register(r'ingredients', IngredientViewSet, basename='ingredients')
router_ver1.register(r'tags', TagViewSet, basename='tags')
router_ver1.register(r'recipes', RecipeViewSet, basename='recipes ')
#router_ver1.register(r'users', UserViewSet, basename='users')

#auth_urls = [
#    path('auth/signup/', SignUpView.as_view()),
#    path('auth/token/', GetTokenView.as_view()),
#]

urlpatterns = [
    path('', include(router_ver1.urls)),
    #path(r'auth/', include(auth_urls)),
]
