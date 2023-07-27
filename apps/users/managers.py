from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ValidationError


class CustomUserManager(BaseUserManager):
    """
    Custom user manager for creating users with email instead of username.
    """

    def create_user(self, email, password, **extra_fields):
        """Create a user from the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        try:
            user.full_clean()
        except ValidationError:
            # handle is taken, make unique
            user.make_handle_unique()
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """Create a superuser from the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        if extra_fields.get("is_active") is not True:
            raise ValueError("Superusers must be activated automatically.")

        return self.create_user(email, password, **extra_fields)
