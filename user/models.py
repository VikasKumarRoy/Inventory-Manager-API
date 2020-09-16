from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.core.validators import RegexValidator
from user.manager import UserManager

from base.models import BaseModel
from organization.models import Organization
from utils import constants


class User(BaseModel, AbstractBaseUser, PermissionsMixin):

    class Meta(BaseModel.Meta, AbstractBaseUser.Meta):
        pass

    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: "
                                                                   "'+999999999'. Up to 15 digits allowed.")

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.PositiveSmallIntegerField(choices=constants.ROLE_CHOICES, default=constants.ROLE.USER)
    date_of_birth = models.DateField(max_length=8, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='images/', blank=True, null=True)
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    address = models.CharField(max_length=500, blank=True, null=True)
    gender = models.PositiveSmallIntegerField(choices=constants.GENDER_CHOICES, blank=True, null=True)

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='employees', null=True, blank=True)

    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.first_name
