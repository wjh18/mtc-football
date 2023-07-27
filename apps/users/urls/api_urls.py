from django.urls import path

from ..views import api_views

app_name = "users"
urlpatterns = [
    # General
    path("whoami/", api_views.WhoAmIView.as_view(), name="api_whoami"),
    path("csrf/", api_views.GetCSRFToken.as_view(), name="api_get_csrf_token"),
    # Users
    path("users/", api_views.UserList.as_view(), name="api_user_list"),
    path(
        "users/<slug:handle>/", api_views.UserDetail.as_view(), name="api_user_detail"
    ),
    # Authentication
    path("signup/", api_views.RegisterUserView.as_view(), name="api_signup"),
    path("login/", api_views.LoginView.as_view(), name="api_login"),
    path("logout/", api_views.LogoutView.as_view(), name="api_logout"),
    path(
        "password/change/",
        api_views.PasswordChangeView.as_view(),
        name="api_password_change",
    ),
    path(
        "password/reset/",
        api_views.PasswordResetView.as_view(),
        name="api_password_reset",
    ),
    path(
        "password/reset/confirm/",
        api_views.PasswordResetConfirmView.as_view(),
        name="api_password_reset_confirm",
    ),
    # Email verification
    path(
        "email/verify/",
        api_views.EmailVerifyView.as_view(),
        name="api_email_verify",
    ),
    path(
        "email/verify/confirm/",
        api_views.EmailVerifyConfirmView.as_view(),
        name="api_email_verify_confirm",
    ),
]
