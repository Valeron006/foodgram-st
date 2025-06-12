from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    avatar = models.ImageField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.email


User = get_user_model()


class SubscriptionRelation(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sub_sender')
    to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sub_to')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['sender', 'to'],
                name='unique_sub'
            )
        ]