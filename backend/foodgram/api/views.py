from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets, mixins, filters
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from foodgram.settings import SHOPPING_LIST_FILENAME
from .filters import RecipeFilter
from recipe.models import (
    FavoritesList,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingList,
    Subscribe,
    Tag,
    User,
)
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    IngredientSerializer,
    RecipeSerializer,
    RecipeCreateSerializer,
    RecipeReadSerializer,
    SubscribeGetSerializer,
    SubscribePostSerializer,
    TagSerializer,
    UserGetSerializer,
    UserPostSerializer,
    PasswordSerializer,
)


class UserViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserGetSerializer
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return UserPostSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def profile(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'],
            permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        serializer = PasswordSerializer(request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({'detail': 'Пароль успешно изменен!'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,),
            pagination_class=PageNumberPagination)
    def subscriptions(self, request):
        queryset = User.objects.filter(subscriber__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscribeGetSerializer(page, many=True,
                                            context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs['pk'])

        if request.method == 'POST':
            serializer = SubscribePostSerializer(
                author, data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(user=request.user, author=author)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            get_object_or_404(Subscribe, user=request.user,
                              author=author).delete()
            return Response({'detail': 'Успешная отписка'},
                            status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny, )
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    permission_classes = (AllowAny, )
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'create', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeCreateSerializer

    def add_or_remove_item(self,
                           model_class,
                           error_message,
                           success_status,
                           **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        serializer = RecipeSerializer(recipe,
                                      data=self.request.data,
                                      context={"request": self.request})
        serializer.is_valid(raise_exception=True)

        if self.request.method == 'POST':
            if not model_class.objects.filter(user=self.request.user,
                                              recipe=recipe).exists():
                model_class.objects.create(user=self.request.user,
                                           recipe=recipe)
                return Response(serializer.data, status=success_status)
            return Response({'errors': error_message},
                            status=status.HTTP_400_BAD_REQUEST)

        if self.request.method == 'DELETE':
            obj = get_object_or_404(model_class,
                                    user=self.request.user,
                                    recipe=recipe)
            obj.delete()
            return Response({'detail': 'Рецепт успешно удален.'},
                            status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, **kwargs):
        return self.add_or_remove_item(
            FavoritesList,
            'Рецепт уже в избранном.',
            status.HTTP_201_CREATED,
            **kwargs
        )

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,),
            pagination_class=None)
    def shopping_cart(self, request, **kwargs):
        return self.add_or_remove_item(
            ShoppingList,
            'Рецепт уже в списке покупок.',
            status.HTTP_201_CREATED,
            **kwargs
        )

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request, **kwargs):
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__shopping_recipe__user=request.user)
            .values('ingredient')
            .annotate(total_amount=Sum('amount'))
            .values_list(
                'ingredient__name',
                'total_amount',
                'ingredient__measurement_unit'
            )
        )
        file_list = ['{} - {} {}.'.format(*ingredient)
                     for ingredient in ingredients]
        file = HttpResponse(
            'Cписок покупок:\n' + '\n'.join(file_list),
            content_type='text/plain'
        )
        file['Content-Disposition'] = (
            f'attachment; filename={SHOPPING_LIST_FILENAME}'
        )
        return file
