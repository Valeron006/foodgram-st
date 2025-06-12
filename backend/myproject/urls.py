"""myproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from menu.views import IngredientListAPIView, IngredientDetailAPIView, RecipeViewSet, view_short_link
from my_user.views import PUserViewSet

from django.conf.urls.static import static

from myproject import settings

router = DefaultRouter()
router.register('', PUserViewSet, basename='users')
router_recipes = DefaultRouter()
router_recipes.register('', RecipeViewSet, basename='recipes')
urlpatterns = [path('admin/', admin.site.urls),
               path('api/auth/', include('djoser.urls.authtoken')),
               path('api/users/', include(router.urls)),
               path('api/recipes/', include(router_recipes.urls)),
               path('api/ingredients/<int:pk>/', IngredientDetailAPIView.as_view(), name='ingredient-detail'),
               path('api/ingredients/', IngredientListAPIView.as_view(), name='ingredient-list'),
               path('s/<str:pk>', view_short_link, name='short-link'),
               ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
