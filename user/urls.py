from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static
from user import views
from rest_framework import routers


router = routers.SimpleRouter()
router.register(r'', views.UserView, basename='user')

urlpatterns = []

urlpatterns += router.urls
