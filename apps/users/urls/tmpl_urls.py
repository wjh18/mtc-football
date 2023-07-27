from django.urls import path

from ..views import tmpl_views

app_name = "users"
urlpatterns = [
    # Profile
    path("users/<slug:handle>/", tmpl_views.UserProfileView.as_view(), name="profile"),
    path(
        "users/<slug:handle>/update/",
        tmpl_views.UpdateHandleView.as_view(),
        name="update_handle",
    ),
    # Authentication
    path("login/", tmpl_views.CustomLoginView.as_view(), name="login"),
    path("logout/", tmpl_views.CustomLogoutView.as_view(), name="logout"),
    path(
        "logout/confirm/", tmpl_views.LogoutConfirmView.as_view(), name="logout_confirm"
    ),
    path("logout/done/", tmpl_views.LogoutDoneView.as_view(), name="logout_done"),
    path("signup/", tmpl_views.SignupView.as_view(), name="signup"),
    path(
        "password_change/",
        tmpl_views.CustomPasswordChangeView.as_view(),
        name="password_change",
    ),
    path(
        "password_change/done/",
        tmpl_views.CustomPasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
    path(
        "password_reset/",
        tmpl_views.CustomPasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        tmpl_views.CustomPasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        tmpl_views.CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        tmpl_views.CustomPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    # Email verification
    path(
        "email/verify/",
        tmpl_views.EmailVerifyView.as_view(),
        name="email_verify",
    ),
    path(
        "email/verify/sent/",
        tmpl_views.EmailVerifySentView.as_view(),
        name="email_verify_sent",
    ),
    path(
        "email/verify/<uidb64>/<token>/",
        tmpl_views.EmailVerifyConfirmView.as_view(),
        name="email_verify_confirm",
    ),
    path(
        "email/verify/done/",
        tmpl_views.EmailVerifyDoneView.as_view(),
        name="email_verify_done",
    ),
]
