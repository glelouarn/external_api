from rest_framework import permissions


class IsAdminOrOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if permissions.IsAdminUser.has_permission(self, request, view):
            return True
        else:
            return obj.owner == request.user