from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.tokens import default_token_generator
from rest_framework import status, viewsets, filters, mixins, generics
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import AccessToken

from foodgram.settings import SHOPPING_LIST_FILENAME
from recipe.models import Ingredient, Recipe, RecipeIngredient, Tag, User, FavoritesList, ShoppingList
from .serializers import (
    IngredientSerializer,
    RecipeSerializer,
    RecipeReadSerializer,
    RecipeCreateSerializer,
    TagSerializer,
    UserSerializer,
    UserGetSerializer,
    UserPostSerializer
)
from .permissions import IsAdminOnly, IsAdminOrReadOnly
from .filters import RecipeFilter


class UserViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserGetSerializer
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return UserGetSerializer
        return UserPostSerializer

    @action(detail=False, methods=['get'],
            pagination_class=None,
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = UserGetSerializer(request.user)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)


class IngredientViewSet(
        mixins.CreateModelMixin,
        mixins.ListModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet
    ):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    search_fields = ('^name', )


class TagViewSet(
        mixins.CreateModelMixin,
        mixins.ListModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet
    ):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = PageNumberPagination
    pagination_class.page_size_query_param = 'limit'
    http_method_names = ['get', 'post', 'patch', 'create', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeCreateSerializer

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        serializer = RecipeSerializer(recipe, context={"request": request})

        if request.method == 'POST':
            if not FavoritesList.objects.filter(user=request.user, recipe=recipe).exists():
                FavoritesList.objects.create(user=request.user, recipe=recipe)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({'errors': 'Рецепт уже в избранном.'}, status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            get_object_or_404(FavoritesList, user=request.user, recipe=recipe).delete()
            return Response({'detail': 'Рецепт успешно удален из избранного.'}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,),
            pagination_class=None)
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        serializer = RecipeSerializer(recipe, context={"request": request})

        if request.method == 'POST':
            if not ShoppingList.objects.filter(user=request.user, recipe=recipe).exists():
                ShoppingList.objects.create(user=request.user, recipe=recipe)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({'errors': 'Рецепт уже в списке покупок.'}, status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            get_object_or_404(ShoppingList, user=request.user, recipe=recipe).delete()
            return Response({'detail': 'Рецепт успешно удален из списка покупок.'}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request, **kwargs):
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__shopping_recipe__user=request.user)
            .values('ingredient')
            .annotate(total_amount=Sum('amount'))
            .values_list('ingredient__name', 'total_amount', 'ingredient__measurement_unit')
        )
        file_list = ['{} - {} {}.'.format(*ingredient) for ingredient in ingredients]
        file = HttpResponse('Cписок покупок:\n' + '\n'.join(file_list), content_type='text/plain')
        file['Content-Disposition'] = f'attachment; filename={SHOPPING_LIST_FILENAME}'
        return file
