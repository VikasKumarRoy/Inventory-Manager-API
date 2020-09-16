from django.db import models
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from invite.serializers import InviteSerializer
from invite.models import Invite
from invite.exceptions import InvitationFailed, InvitationExpired
from invite.permissions import IsAdmin
from base.token_expire_handler import is_token_expired


class InviteView(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = (IsAdmin,)

    serializer_class = InviteSerializer
    queryset = Invite.objects.all()
    lookup_field = 'id'

    def get_object(self):
        invite_token = self.kwargs.get('id')
        try:
            invite = Invite.objects.get(key=invite_token)
        except models.ObjectDoesNotExist:
            raise InvitationFailed
        is_expired = is_token_expired(invite)
        if is_expired:
            raise InvitationExpired
        return invite


