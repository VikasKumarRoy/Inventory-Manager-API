from django.conf.urls import url, include
from item import views
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'', views.ItemGroupView, basename='item-group')

item_router = routers.SimpleRouter()
item_router.register(r'', views.ItemView, basename='item')

request_router = routers.SimpleRouter()
request_router.register(r'', views.RequestedItemView, basename='requested-item')

history_router = routers.SimpleRouter()
history_router.register(r'', views.ItemHistoryView, basename='history-item')

urlpatterns = [
    url(r'^(?P<item_group_id>\d+)/item/', include(item_router.urls)),
    url(r'^(?P<item_group_id>\d+)/request/', include(request_router.urls)),
    url(r'^(?P<item_group_id>\d+)/item/(?P<item_id>\d+)/history/', include(history_router.urls)),
]

urlpatterns += router.urls
