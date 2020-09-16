from django.contrib import admin
from base.model_admin import BaseModelAdmin
from organization.models import Organization


class OrganizationAdmin(BaseModelAdmin):
    pass


admin.site.register(Organization, OrganizationAdmin)
