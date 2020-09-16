from django.conf.urls import url, include
from item import views
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'', views.ManageRequestView, basename='')

approve_router = routers.SimpleRouter()
approve_router.register(r'', views.ApprovedItemView, basename='')

urlpatterns = [
    url(r'^(?P<request_id>\d+)/item/(?P<item_id>\d+)/approve/', include(approve_router.urls)),
]

urlpatterns += router.urls
