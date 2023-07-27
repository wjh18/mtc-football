from django.contrib.auth import get_user_model
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework import generics, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..mixins import ActionsMetadataMixin
from ..permissions import IsSelfOrAdminUser
from ..serializers import (
    EmailVerifyConfirmSerializer,
    EmailVerifySerializer,
    LoginSerializer,
    PasswordChangeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetSerializer,
    RegisterUserSerializer,
    UserSerializer,
)

CustomUser = get_user_model()


class UserList(generics.ListAPIView):
    """Lists all users with user info for admin purposes."""

    queryset = CustomUser.objects.all()
    permission_classes = (IsAdminUser,)
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    """Retrieves a user's info for admins or as a private user profile."""

    queryset = CustomUser.objects.all()
    permission_classes = (IsSelfOrAdminUser,)
    serializer_class = UserSerializer
    lookup_field = "handle"


@method_decorator(sensitive_post_parameters(), name="dispatch")
class RegisterUserView(generics.CreateAPIView):
    """Registers a user based on the information they provide."""

    model = CustomUser
    permission_classes = [~IsAuthenticated & AllowAny]
    serializer_class = RegisterUserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = {
            "success": _("User registration successful. Verification email sent."),
            "email": email,
        }
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


@method_decorator(ensure_csrf_cookie, name="dispatch")
class GetCSRFToken(APIView):
    """Retrieves a CSRF token and sets it as a cookie."""

    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        return Response({"success": _("CSRF cookie set")})


@method_decorator(sensitive_post_parameters(), name="dispatch")
class LoginView(APIView, ActionsMetadataMixin):
    """Authenticates a user and sets their session cookie."""

    authentication_classes = (SessionAuthentication,)
    permission_classes = [~IsAuthenticated & AllowAny]
    # Manually specify serializer class to surface HTML form in Browsable API
    serializer_class = LoginSerializer  # Not a default field of APIView

    def post(self, request, format=None):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        django_login(request, user)
        data = {"success": _("Login successful.")}
        return Response(data, status=status.HTTP_202_ACCEPTED)


class LogoutView(APIView):
    """Logs a user out and clears their session."""

    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        django_logout(request)
        data = {"success": _("Logout successful.")}
        return Response(data, status=status.HTTP_200_OK)


class WhoAmIView(APIView):
    """Checks if a user is authenticated via their session."""

    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


@method_decorator(sensitive_post_parameters(), name="dispatch")
class PasswordChangeView(APIView, ActionsMetadataMixin):
    """Changes a user's password and clears their session."""

    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)
    # Manually specify serializer class to surface HTML form in Browsable API
    serializer_class = PasswordChangeSerializer  # Not a default field of APIView

    def post(self, request, format=None):
        serializer = self.serializer_class(
            data=request.data, context={"user": request.user}
        )
        serializer.is_valid(raise_exception=True)
        data = {"success": _("Password change successful. Please login again.")}
        return Response(data, status=status.HTTP_200_OK)


class PasswordResetView(APIView, ActionsMetadataMixin):
    """Requests a password reset email for a user."""

    permission_classes = (AllowAny,)
    serializer_class = PasswordResetSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        # Avoid raising exceptions so emails can't be guessed
        if serializer.is_valid(raise_exception=False):
            # Only save serializer if reset form is valid
            serializer.save()
        data = {"detail": _("Password reset email requested.")}
        return Response(data, status=status.HTTP_200_OK)


@method_decorator(sensitive_post_parameters(), name="dispatch")
class PasswordResetConfirmView(APIView, ActionsMetadataMixin):
    """Confirms a user's password reset and resets their password."""

    permission_classes = (AllowAny,)
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = {"success": _("Password reset successful.")}
        return Response(data, status=status.HTTP_200_OK)


class EmailVerifyView(APIView, ActionsMetadataMixin):
    """Requests an email verification email for a user."""

    permission_classes = (AllowAny,)
    serializer_class = EmailVerifySerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()  # Send verification email
        data = {"success": _("Verification email requested.")}
        return Response(data, status=status.HTTP_200_OK)


@method_decorator(sensitive_post_parameters(), name="dispatch")
class EmailVerifyConfirmView(APIView, ActionsMetadataMixin):
    """Confirms a user's email verification and activates their account."""

    permission_classes = (AllowAny,)
    serializer_class = EmailVerifyConfirmSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()  # Activate the user
        data = {"success": _("Email verification successful.")}
        return Response(data, status=status.HTTP_200_OK)
