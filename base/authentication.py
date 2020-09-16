from django.db.models import ObjectDoesNotExist
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

from authentication.models import AuthToken
from base.token_expire_handler import is_token_expired


class BaseTokenAuthentication(TokenAuthentication):
    model = AuthToken

    def authenticate_credentials(self, key):
        try:
            token = AuthToken.objects.select_related('user').get(key=key)
        except ObjectDoesNotExist:
            raise AuthenticationFailed('Invalid token')

        if not token.user.is_active:
            raise AuthenticationFailed('User inactive or deleted.')

        is_expired = is_token_expired(token)
        if is_expired:
            raise AuthenticationFailed('Authentication token expired')
        return token.user, token
