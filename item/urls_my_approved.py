from django.conf.urls import url, include
from item import views
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'', views.MyApproved, basename='')

urlpatterns = []

urlpatterns += router.urls
