from django.contrib import admin
from base.model_admin import BaseModelAdmin
from invite.models import Invite


class InviteAdmin(BaseModelAdmin):
    pass


admin.site.register(Invite, InviteAdmin)
