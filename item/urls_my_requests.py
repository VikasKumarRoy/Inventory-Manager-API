from item import views
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'', views.MyRequests, basename='')

urlpatterns = []

urlpatterns += router.urls
