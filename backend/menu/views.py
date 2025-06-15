from http import HTTPStatus

from django.urls import reverse
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import redirect
from django_filters.rest_framework import DjangoFilterBackend

from menu.models import ShortLink
from menu.serializers import *
from django_filters import FilterSet, CharFilter, NumberFilter


class RecipePagination(PageNumberPagination):
    page_size = 8
    page_size_query_param = 'limit'
    max_page_size = 100


class RecipeFilter(FilterSet):
    author = NumberFilter(field_name='author__id')
    is_in_shopping_cart = NumberFilter(method='filter_is_in_shopping_cart')
    is_favorited = NumberFilter(method='filter_is_favorited')

    class Meta:
        model = Recipe
        fields = ['author']

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shopping_cart_recipe__user=user)
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorites__user=user)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeListSerializer
    pagination_class = RecipePagination
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_class = RecipeFilter

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_serializer_class(self):
        if self.action.lower() == 'get':
            return RecipeListSerializer
        else:
            return RecipeCreateUpdateSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            return Response(status=HTTPStatus.FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=HTTPStatus.NO_CONTENT)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, _, pk=None):
        inst = ShortLink(recipe_id=pk)
        inst.save()
        return Response({'short-link': reverse('short-link', kwargs={'pk': inst.id})})

    @action(detail=True, methods=['post', 'delete'], url_path='favorite')
    def favorite(self, request, pk=None):
        try:
            recipe = Recipe.objects.get(pk=pk)
        except:
            return Response(status=HTTPStatus.NOT_FOUND)
        if request.method == 'POST':
            obj, created = FavoriteRelation.objects.get_or_create(user=request.user, recipe=recipe)
            if not created:
                return Response(status=HTTPStatus.BAD_REQUEST)
            serializer = RecipeShortSerializer(recipe, context={'request': request})
            return Response(serializer.data, status=HTTPStatus.CREATED)
        if request.method == 'DELETE':
            favorite = request.user.favorites.filter(recipe=recipe).first()
            if not favorite:
                return Response(status=HTTPStatus.BAD_REQUEST)
            favorite.delete()
            return Response(status=HTTPStatus.NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'], url_path='shopping_cart')
    def shopping_cart(self, request, pk=None):
        try:
            recipe = Recipe.objects.get(pk=pk)
        except:
            return Response(status=HTTPStatus.NOT_FOUND)
        if request.method == 'POST':
            obj, created = ShoppingCartRelation.objects.get_or_create(user=request.user, recipe=recipe)
            if not created:
                return Response(status=HTTPStatus.BAD_REQUEST)
            serializer = RecipeShortSerializer(recipe, context={'request': request})
            return Response(serializer.data, status=HTTPStatus.CREATED)
        if request.method == 'DELETE':
            deleted_count, _ = request.user.shopping_cart.filter(recipe=recipe).delete()
            if deleted_count == 0:
                return Response(status=HTTPStatus.BAD_REQUEST)
            return Response(status=HTTPStatus.NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        ingredients = request.user.shopping_cart.all().values_list(
            'recipe__recipe_ingredients__ingredient__name',
            'recipe__recipe_ingredients__ingredient__measurement_unit',
            'recipe__recipe_ingredients__amount'
        )

        shopping_list = {}
        for name, unit, amount in ingredients:
            if name not in shopping_list:
                shopping_list[name] = {'amount': 0, 'unit': unit}
            shopping_list[name]['amount'] += amount

        text_content = "Список покупок:\n\n"
        for name, data in shopping_list.items():
            text_content += f"{name} - {data['amount']} {data['unit']}\n"

        response = Response(text_content, content_type='text/plain', status=HTTPStatus.OK)
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response


def view_short_link(request, pk):
    return redirect('recipes-detail', pk=ShortLink.objects.get(recipe_id=pk).id)


class IngredientFilter(FilterSet):
    name = CharFilter(lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ['name']


class IngredientListAPIView(generics.ListAPIView):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


class IngredientDetailAPIView(generics.RetrieveAPIView):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
