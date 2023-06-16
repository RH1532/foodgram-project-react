from django_filters.rest_framework import FilterSet, filters
from recipe.models import Recipe, Tag


class RecipeFilter(FilterSet):
    is_favorited = filters.BooleanFilter(
        field_name='favorite_recipe__user',
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='shopping_recipe__user',
        method='filter_is_in_shopping_cart'
    )
    author = filters.NumberFilter(field_name='author_id')
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')

    def filter_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorite_recipe__isnull=False)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(shopping_recipe__isnull=False)
        return queryset
