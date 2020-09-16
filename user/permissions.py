from rest_framework import exceptions
from rest_framework.permissions import BasePermission

from utils.constants import ROLE


class IsAdminOrManager(BasePermission):

    def has_permission(self, request, view):
        actions = ['destroy', 'list']
        if view.action in actions:
            return request.user.is_authenticated and (request.user.role in (ROLE.ADMIN, ROLE.MANAGER,))
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if view.action == 'retrieve':
            return request.user.role != ROLE.USER or obj.id == request.user.id
        elif view.action == 'update':
            return obj.id == request.user.id
