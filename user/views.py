from rest_framework import viewsets, mixins

from user.models import User
from user.permissions import IsAdminOrManager
from user.serializers import UserSerializer


class UserView(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = UserSerializer
    lookup_field = 'id'
    permission_classes = (IsAdminOrManager,)

    def get_queryset(self):
        return User.objects.filter(organization=self.request.user.organization)

