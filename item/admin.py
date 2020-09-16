from django.contrib import admin
from base.model_admin import BaseModelAdmin
from item.models import ItemGroup, Item, ItemAttribute, RequestedItem, ApprovedItem, ItemHistory


class ItemAdmin(BaseModelAdmin):
    pass


admin.site.register(ItemGroup, ItemAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(ItemAttribute, ItemAdmin)
admin.site.register(RequestedItem, ItemAdmin)
admin.site.register(ApprovedItem, ItemAdmin)
admin.site.register(ItemHistory, ItemAdmin)
