from datetime import timedelta
from django.utils import timezone
from django.conf import settings

from authentication.models import AuthToken
from invite.models import Invite


def expires_in(token):
    time_elapsed = timezone.now() - token.created_at
    time_left = 0
    if isinstance(token, AuthToken):
        time_left = timedelta(seconds=settings.AUTH_TOKEN_EXPIRES_AFTER_SECONDS) - time_elapsed
    elif isinstance(token, Invite):
        time_left = timedelta(seconds=settings.INVITE_TOKEN_EXPIRES_AFTER_SECONDS) - time_elapsed
    return time_left


def is_token_expired(token):
    return expires_in(token) < timedelta(seconds=0)
