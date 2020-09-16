from django.db import models
from base.models import BaseModel


class Organization(BaseModel):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
