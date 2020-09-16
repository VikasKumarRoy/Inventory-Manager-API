from django.urls import reverse, resolve
from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.auth.hashers import make_password

from ddf import G, F

from invite.models import Invite
from user.models import User
from authentication.models import AuthToken
from item.models import ItemGroup, Item, RequestedItem, ApprovedItem
from utils.constants import ROLE


class ItemTests(APITestCase):

    def test_item_group(self):
        url = reverse('item:item-group-list')
        print(url)
