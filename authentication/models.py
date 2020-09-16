from django.db import models

from base.models import BaseModel
from user.models import User
from utils import helpers


class AuthToken(BaseModel):
    key = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tokens')

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = helpers.generate_key()
        return super().save(*args, **kwargs)
