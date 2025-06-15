from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='Электронная почта')
    avatar = models.ImageField(null=True, blank=True, verbose_name='Аватар')
    first_name = models.CharField(max_length=150, verbose_name='Имя')
    last_name = models.CharField(max_length=150, verbose_name='Фамилия')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ('email', 'username', 'first_name', 'last_name')
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email


User = get_user_model()


class SubscriptionRelation(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sub_sender',
        verbose_name='Подписчик'
    )
    to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sub_to',
        verbose_name='Автор'
    )

    class Meta:
        ordering = (
            'sender__username', 'to__username'
        )
        constraints = [
            models.UniqueConstraint(
                fields=['sender', 'to'],
                name='unique_sub'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return str(self.sender)
