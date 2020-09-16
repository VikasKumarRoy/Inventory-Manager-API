from django.contrib import admin
from base.model_admin import BaseModelAdmin
from user.models import User


class UserAdmin(BaseModelAdmin):
    pass


admin.site.register(User, UserAdmin)
