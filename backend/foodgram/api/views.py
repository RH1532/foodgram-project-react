from django.db.models import Sum, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets, mixins
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
from .permissions import IsAdminOrReadOnly
from .serializers import (
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeReadSerializer,
    SubscribeSerializer,
    TagSerializer,
    UserGetSerializer,
    UserPostSerializer,
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

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        queryset = Subscribe.objects.filter(user=request.user)
        serializer = SubscribeSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(detail=True, methods=['post'],
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs['pk'])
        serializer = SubscribeSerializer(
            data={'user': request.user.id, 'author': author.id},
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'],
            permission_classes=(IsAuthenticated,))
    def unsubscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs['pk'])
        subscription = get_object_or_404(Subscribe,
                                         Q(user=request.user)
                                         & Q(author=author))
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    search_fields = ('^name', )


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'create', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeCreateSerializer

    def add_or_remove_item(request,
                           model_class,
                           error_message,
                           success_status,
                           **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])

        if request.method == 'POST':
            if not model_class.objects.filter(user=request.user,
                                              recipe=recipe).exists():
                model_class.objects.create(user=request.user, recipe=recipe)
                return Response(status=success_status)
            return Response({'errors': error_message},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            get_object_or_404(model_class,
                              user=request.user,
                              recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, **kwargs):
        return self.add_or_remove_item(
            request,
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
            request,
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
