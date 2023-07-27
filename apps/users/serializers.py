from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode as uid_decoder
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .tokens import email_verification_token, send_email_verification
from .utils import validate_user_password

CustomUser = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("email", "is_staff", "date_joined", "last_login", "is_active")


class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)
    confirm_password = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )

    user = None

    class Meta:
        model = CustomUser
        fields = ("email", "password", "confirm_password")

    def create(self, validated_data):
        self.user = CustomUser.objects.create_user(
            email=validated_data["email"], password=validated_data["password"]
        )
        self._send_email_verification()
        return self.user

    def validate(self, attrs):
        """Validate that the passwords match"""
        email = attrs.get("email")
        password = attrs.get("password")
        # Confirm password isn't needed for create user
        confirm_password = attrs.pop("confirm_password")

        if email and password and confirm_password:
            if password != confirm_password:
                msg = {
                    "password": _("Passwords must match."),
                    "confirm_password": _("Passwords must match."),
                }
                raise serializers.ValidationError(msg)

            # Temporary user needed to validate pw
            temp_user = CustomUser(email=email, password=password)
            validate_user_password(temp_user, password, "password")

        else:
            msg = _('Must include "email", "password" and "confirm_password".')
            raise serializers.ValidationError(msg)

        return attrs

    def _send_email_verification(self):
        request = self.context.get("request")
        # Set some values to pass to the email_user method.
        opts = {
            "use_https": request.is_secure(),
            "from_email": getattr(settings, "DEFAULT_FROM_EMAIL"),
        }
        send_email_verification(self.user, **opts)


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = CustomUser
        fields = ("email", "password")

    def validate(self, attrs):
        """Validate the user's credentials"""
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(self.context["request"], email=email, password=password)
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg)

        if not user:
            msg = _(
                "Unable to log in with the provided credentials."
                " Is your account verified?"
            )
            raise serializers.ValidationError(msg)

        attrs["user"] = user
        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)
    new_password = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )
    confirm_new_password = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )

    def validate(self, attrs):
        user = self.context["user"]
        password = attrs.get("password")
        new_password = attrs.get("new_password")
        confirm_new_password = attrs.get("confirm_new_password")

        if password and new_password and confirm_new_password:
            if not user.check_password(password):
                msg = {"password": _("Invalid old password supplied.")}
                raise serializers.ValidationError(msg)

            if new_password != confirm_new_password:
                msg = {
                    "new_password": _("Passwords must match."),
                    "confirm_new_password": _("Passwords must match."),
                }
                raise serializers.ValidationError(msg)

            validate_user_password(user, new_password, "new_password")
        else:
            msg = _(
                'Must include "password", "new_password" and "confirm_new_password".'
            )
            raise serializers.ValidationError(msg)

        # Change password if validations pass
        user.set_password(new_password)
        user.save()

        return attrs


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)

    reset_form = None

    def validate(self, attrs):
        email = attrs.get("email")
        self.reset_form = PasswordResetForm(data={"email": email})
        if not self.reset_form.is_valid():
            raise serializers.ValidationError(self.reset_form.errors)
        return attrs

    def save(self):
        request = self.context.get("request")
        # Set some values to trigger the send_email method.
        opts = {
            "use_https": request.is_secure(),
            "from_email": getattr(settings, "DEFAULT_FROM_EMAIL"),
            "request": request,
        }
        self.reset_form.save(**opts)


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password1 = serializers.CharField(
        style={"input_type": "password"}, write_only=True, label="New password"
    )
    new_password2 = serializers.CharField(
        style={"input_type": "password"}, write_only=True, label="Confirm new password"
    )
    uid = serializers.CharField(label="User ID")
    token = serializers.CharField()

    set_password_form = None

    def validate(self, attrs):
        try:
            uid = force_str(uid_decoder(attrs["uid"]))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            msg = {"uid": _("Unable to reset password. User error.")}
            raise serializers.ValidationError(msg)

        if not default_token_generator.check_token(user, attrs["token"]):
            msg = {"token": _("Unable to reset password. Invalid token.")}
            raise serializers.ValidationError(msg)

        self.set_password_form = SetPasswordForm(user=user, data=attrs)

        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(self.set_password_form.errors)

        return attrs

    def save(self):
        self.set_password_form.save()


class EmailVerifySerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)

    user = None

    def validate(self, attrs):
        email = attrs.get("email")
        gen_err = _("Unable to send verification email.")

        try:
            self.user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            msg = {"email": _(f"{gen_err} User does not exist.")}
            raise serializers.ValidationError(msg)

        if self.user is not None and self.user.is_active:
            msg = {"email": _(f"{gen_err} User already active.")}
            raise serializers.ValidationError(msg)

        return attrs

    def save(self):
        request = self.context.get("request")
        # Set some values to pass to the email_user method.
        opts = {
            "use_https": request.is_secure(),
            "from_email": getattr(settings, "DEFAULT_FROM_EMAIL"),
        }
        send_email_verification(self.user, **opts)


class EmailVerifyConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField(label="User ID")
    token = serializers.CharField()

    user = None

    def validate(self, attrs):
        gen_err = _("Unable to activate account.")

        try:
            uid = force_str(uid_decoder(attrs["uid"]))
            self.user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            msg = {"uid": _(f"{gen_err} User error.")}
            raise serializers.ValidationError(msg)

        if self.user is None or not email_verification_token.check_token(
            self.user, attrs["token"]
        ):
            msg = {"token": _(f"{gen_err} Invalid token.")}
            raise serializers.ValidationError(msg)

        if self.user is not None and self.user.is_active:
            msg = {"email": _(f"{gen_err} User already active.")}
            raise serializers.ValidationError(msg)

        return attrs

    def save(self):
        self.user.is_active = True
        self.user.save()
