from django.contrib.auth.mixins import LoginRequiredMixin


class ActionsMetadataMixin:
    """Surfaces `actions` metadata in OPTIONS request using SimpleMetadata.

    APIView doesn't have a `get_serializer` method by default. Which causes
    the `SimpleMetadata.determine_actions` method to not be run.
    """

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(*args, **kwargs)


class SelfOrAdminRequiredMixin(LoginRequiredMixin):
    """
    Permits a user to view their own profile or admins to view anyone's profile.

    For use in Django generic views only.
    """

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        user = self.request.user
        if user.is_staff:
            return queryset
        return queryset.filter(pk=user.pk)

    def test_func(self):
        return super().test_func()
