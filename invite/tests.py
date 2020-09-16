from django.urls import reverse, resolve
from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.auth.hashers import make_password

from ddf import G, F

from invite.models import Invite
from user.models import User
from authentication.models import AuthToken

from utils.constants import ROLE


class InviteTests(APITestCase):

    def setup(self):
        G(AuthToken, user=F(email="kashish25798@gmail.com", password=make_password("qwerty123456789"), role=ROLE.ADMIN,
                            organization__name="JTG"))

    def test_invite_with_http_header(self):
        self.setup()
        url = reverse("invite:invite-list")
        auth_headers = {'HTTP_AUTHORIZATION': 'Token ' + AuthToken.objects.get().key}
        data = {"email": "kashish25798@gmail.com", "first_name": "Kashish", "last_name": "Sharma", "role": ROLE.ADMIN}
        response = self.client.post(path=url, data=data, **auth_headers)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(Invite.objects.count(), 1)

    def test_invite_without_http_header(self):
        url = reverse("invite:invite-list")
        data = {"email": "kashish25798@gmail.com", "first_name": "Kashish", "last_name": "Sharma", "role": ROLE.ADMIN}
        response = self.client.post(path=url, data=data)
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEquals(Invite.objects.count(), 0)

    def test_invite_invalid_http_header(self):
        url = reverse("invite:invite-list")
        auth_headers = {'HTTP_AUTHORIZATION': 'Token 123456789'}
        data = {"email": "kashish25798@gmail.com", "first_name": "Kashish", "last_name": "Sharma", "role": ROLE.ADMIN}
        response = self.client.post(path=url, data=data, **auth_headers)
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEquals(Invite.objects.count(), 0)
