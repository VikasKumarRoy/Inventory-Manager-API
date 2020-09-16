from rest_framework.permissions import BasePermission
from rest_framework import exceptions
from utils import constants


class IsAdmin(BasePermission):

    def has_permission(self, request, view):
        if view.action == 'create':
            if not request.user.is_authenticated:
                raise exceptions.PermissionDenied()
            if not hasattr(request.user, 'role'):
                raise exceptions.PermissionDenied('User is not assigned any role')
            return request.user and request.user.role == constants.ROLE.ADMIN
        elif view.action == 'retrieve':
            return True
        return exceptions.MethodNotAllowed
