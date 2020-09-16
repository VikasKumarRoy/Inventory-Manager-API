from django.urls import reverse, resolve
from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.auth.hashers import make_password

from ddf import G

from user.models import User
from authentication.models import AuthToken

from utils.constants import ROLE


class LoginTests(APITestCase):

    def setUp(self):
        G(User, email="kashish25798@gmail.com", password=make_password("qwerty123456789"), role=ROLE.ADMIN,
          organization__name="JTG")

    def test_login_correct_credentials(self):
        url = reverse('authentication:authentication-login')
        data = {"email": "kashish25798@gmail.com", "password": "qwerty123456789"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(AuthToken.objects.count(), 1)

    def test_login_incorrect_credentials(self):
        url = reverse('authentication:authentication-login')
        data = {"email": "kashish@gmail.com", "password": "qwerty123456789"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(AuthToken.objects.count(), 0)

    def test_login_missing_credentials(self):
        url = reverse('authentication:authentication-login')
        data = {"password": "qwerty123456789"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(AuthToken.objects.count(), 0)
