from django.contrib import admin
from django.contrib.auth import get_user_model

from my_user.models import SubscriptionRelation

admin.site.register(SubscriptionRelation)
admin.site.register(get_user_model())
