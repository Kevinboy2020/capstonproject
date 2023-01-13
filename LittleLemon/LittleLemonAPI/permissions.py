from rest_framework import permissions


class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        manager = request.user.groups.filter(name='Manager').exists()
        return manager
