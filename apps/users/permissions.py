from django.contrib.auth.mixins import UserPassesTestMixin
from rest_framework import permissions


class IsSelfOrAdminUser(permissions.BasePermission):
    """Permits a user (or admins) to access their own user data.

    For use in DRF views only.
    """

    def has_object_permission(self, request, view, obj):
        if request.user:
            if request.user.is_staff:
                return True
            return obj == request.user
        return False


class SelfOrAdminRequiredMixin(UserPassesTestMixin):
    """Permits a user (or admins) to view their own profile.

    For use in Django generic views only.
    """

    def test_func(self):
        user = self.request.user
        return user.is_staff or user == self.get_object()
