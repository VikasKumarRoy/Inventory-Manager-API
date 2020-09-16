from django.conf.urls import url, include
from authentication import views
from rest_framework import routers


router = routers.SimpleRouter()
router.register(r'', views.AuthView, basename='authentication')

urlpatterns = []

urlpatterns += router.urls
