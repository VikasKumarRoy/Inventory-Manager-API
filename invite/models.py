from django.db import models
from base.models import BaseModel
from user.models import User
from utils import helpers, constants


class Invite(BaseModel):

    key = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=100)
    role = models.PositiveSmallIntegerField(choices=constants.ROLE_CHOICES, default=constants.ROLE.USER)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    admin = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = helpers.generate_key()
        return super().save(*args, **kwargs)

    def __str__(self):
        return "{id} {first_name}".format(id=self.id, first_name=self.first_name)
