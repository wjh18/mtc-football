from django.contrib.auth.mixins import UserPassesTestMixin


class SuperuserRequiredMixin(UserPassesTestMixin):
    """
    Limit a view to superusers only.
    """

    def test_func(self):
        return self.request.user.is_superuser
