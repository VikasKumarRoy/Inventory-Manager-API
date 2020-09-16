from rest_framework import status
from rest_framework.exceptions import APIException


class InvitationFailed(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Invalid invite token.'
    default_code = 'invitation_failed'


class InvitationExpired(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Invite token expired.'
    default_code = 'invitation_failed'
