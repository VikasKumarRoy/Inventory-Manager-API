from rest_framework import exceptions
from rest_framework.permissions import BasePermission

from utils.constants import ROLE


class IsAdminOrManagerActions(BasePermission):

    def has_permission(self, request, view):
        actions = ['create', 'update', 'destroy', 'send_reminder']
        if view.action in actions:
            return request.user.is_authenticated and (request.user.role in (ROLE.ADMIN, ROLE.MANAGER,))
        elif view.action == 'user':
            return request.user.is_authenticated and request.user.role == ROLE.USER
        return request.user.is_authenticated
    

class IsAdminOrManager(BasePermission):

    def has_permission(self, request, view):
        return request.user.role in (ROLE.ADMIN, ROLE.MANAGER,)
