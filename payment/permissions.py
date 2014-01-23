from rest_framework import permissions


class IsAdminOrOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if self.has_permission(request, view):
            return True
        else:
            return obj.owner == request.user