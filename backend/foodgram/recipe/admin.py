from django.contrib import admin
from .models import (
    User,
    Subscribe,
    Ingredient,
    Tag,
    Recipe,
    RecipeIngredient,
    FavoritesList,
    ShoppingList
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'username',
        'email',
        'password',
        'is_superuser',
        'first_name',
        'last_name',
    )
    list_editable = ('password', )
    list_filter = ('username', 'email')
    search_fields = ('username',)
    empty_value_display = '-пусто-'


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'author',
    )
    list_editable = ('user', 'author')
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'unit',
    )
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'color',
        'slug',
    )
    list_editable = (
        'name',
        'color',
        'slug',
    )
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'author',
        'name',
        'image',
        'text',
        'cooking_time',
        'in_favorites',
    )
    list_editable = (
        'name',
        'image',
        'text',
        'cooking_time',
    )
    readonly_fields = ('in_favorites',)
    list_filter = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'

    @admin.display(description='В избранном')
    def in_favorites(self, obj):
        return obj.favorite_recipe.count()


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'recipe',
        'ingredient',
        'amount',
    )
    list_editable = (
        'recipe',
        'ingredient',
        'amount',
    )


@admin.register(FavoritesList)
class FavoritesListAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'recipe',
    )
    list_editable = (
        'user',
        'recipe',
    )


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'recipe',
    )
    list_editable = (
        'user',
        'recipe',
    )
