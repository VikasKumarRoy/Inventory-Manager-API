from django.conf.urls import url, include

from item import views
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'', views.MyOrganizationRequests, basename='')

approved_router = routers.SimpleRouter()
approved_router.register(r'', views.MyOrganizationApprovedRequests, basename='approved-request')

urlpatterns = [
    url(r'^approved/', include(approved_router.urls)),
]

urlpatterns += router.urls
