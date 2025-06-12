from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from djoser.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from django.core.files.base import ContentFile
import base64
import uuid
from django.shortcuts import get_object_or_404

from my_user.models import SubscriptionRelation
from my_user.serializers import AvatarSerializer, CustomUserCreateSerializer
from menu.serializers import SubscribedSerializer
from rest_framework.exceptions import ValidationError, ParseError, NotFound, PermissionDenied

User = get_user_model()


class PUserViewSet(UserViewSet):
    pagination_class = LimitOffsetPagination

    @action(detail=False, methods=['get'], url_path='subscriptions')
    def subscriptions(self, request):
        subscriptions = SubscriptionRelation.objects.filter(sender=request.user)
        page = self.paginate_queryset([sub.to for sub in subscriptions])
        if page != 0:
            serializer = SubscribedSerializer(page,
                                              many=True,
                                              context={'request': request})
            return self.get_paginated_response(serializer.data)
        else:
            serializer = SubscribedSerializer([sub.to for sub in subscriptions],
                                              many=True,
                                              context={'request': request})
            return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe')
    def subscribe(self, request, id=None):
        user_to_follow = get_object_or_404(User, pk=id)
        current_user = request.user
        if not current_user.is_authenticated:
            return Response({'message': 'Требуется авторизация'},
                            status=status.HTTP_403_FORBIDDEN)
        if request.method == 'POST':
            if current_user == user_to_follow:
                return Response({'message': 'Подписка на себя невозможна'},
                                status=status.HTTP_409_CONFLICT)
            if SubscriptionRelation.objects.filter(sender=current_user, to=user_to_follow).exists():
                return Response({'message': 'Подписка уже существует'},
                                status=status.HTTP_208_ALREADY_REPORTED)
            SubscriptionRelation.objects.create(sender=current_user,
                                                to=user_to_follow)
            serializer = SubscribedSerializer(user_to_follow, context={'request': request})
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            follow_relation = SubscriptionRelation.objects.filter(
                sender=current_user,
                to=user_to_follow
            )
            if not follow_relation.exists():
                return Response({'message': 'Подписка не найдена'},
                                status=status.HTTP_404_NOT_FOUND)
            follow_relation.delete()
            return Response({'message': 'Подписка удалена'},
                            status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='me', permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = CustomUserCreateSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get', 'put', 'delete'], url_path='me/avatar', permission_classes=[IsAuthenticated])
    def me_avatar(self, request):
        if request.method == 'GET':
            serializer = AvatarSerializer(request.user)
            return Response(serializer.data)
        if request.method == 'PUT':
            avatar_data = request.data.get('avatar')
            user = request.user
            if not avatar_data:
                raise ValidationError()
            try:
                extension, avatar_data = avatar_data.split(';base64,')
                extension = extension.split("/")[-1]
            except:
                raise ParseError
            if avatar_data:
                user.avatar.save(str(uuid.uuid4()) + '.' + extension, ContentFile(base64.b64decode(avatar_data)))
                user.save()
            avatar = None
            if user.avatar:
                avatar = request.build_absolute_uri(user.avatar.url)
            return Response({'avatar': avatar}, status=status.HTTP_200_OK)
        if request.method == 'DELETE':
            if request.user.is_authenticated and request.user.avatar:
                request.user.avatar.delete()
                request.user.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                raise NotFound('Аватар не найден ')

    @action(detail=False, methods=['post'], url_path='set_password', permission_classes=[IsAuthenticated])
    def set_password(self, request):
        if not request.user.is_authenticated:
            raise PermissionDenied
        serializer = settings.SERIALIZERS.set_password(data=request.user.data)
        if not serializer.is_valid():
            raise ValidationError
        request.user.set_password(serializer.data["new_password"])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
