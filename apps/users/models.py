from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from apps.core.utils import random_string_generator

from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model with certain fields and methods copied over from
    AbstractUser, but with email as the unique identifier and no username.
    """

    email = models.EmailField(_("email address"), unique=True)
    # Set blank=True so createsuperuser/forms don't require handle (auto gen)
    # Using blank=True and null=False requires field value to be auto gen
    handle = models.SlugField(_("user handle"), blank=True, null=False, unique=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=False,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # `handle` is not required (blank != False)

    objects = CustomUserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.handle

    def clean(self):
        if self._state.adding:
            # Only run during user creation
            self.handle = self._generate_handle_from_email(self.email)

    def _generate_handle_from_email(self, email) -> str:
        try:
            local_part = email.strip().rsplit("@", 1)[0]
        except ValueError:
            local_part = email

        handle = slugify(local_part)

        return handle

    def make_handle_unique(self):
        self.handle += f"-{random_string_generator()}"

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Send an email to this user.

        Helpful method from AbstractUser that's not included in AbstractBaseUser.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)
