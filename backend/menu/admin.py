from django.contrib import admin

from menu.models import Ingredient, Recipe, RecipeIngredient, FavoriteRelation, ShoppingCartRelation

admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(RecipeIngredient)
admin.site.register(FavoriteRelation)
admin.site.register(ShoppingCartRelation)
