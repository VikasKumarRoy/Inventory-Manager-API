from django.conf.urls import url, include
from invite import views
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'', views.InviteView, basename='invite')

urlpatterns = []

urlpatterns += router.urls

