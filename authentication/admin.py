from django.contrib import admin
from base.model_admin import BaseModelAdmin
from authentication.models import AuthToken


class AuthTokenAdmin(BaseModelAdmin):
    pass


admin.site.register(AuthToken, AuthTokenAdmin)
