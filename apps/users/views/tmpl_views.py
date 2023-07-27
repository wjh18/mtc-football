from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, views
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode as uid_decoder
from django.views import generic
from django.views.decorators.debug import sensitive_post_parameters

from ..forms import CustomUserCreationForm, EmailVerifyConfirmForm, EmailVerifyForm
from ..mixins import SelfOrAdminRequiredMixin
from ..tokens import email_verification_token, send_email_verification

CustomUser = get_user_model()


class CustomLoginView(SuccessMessageMixin, views.LoginView):
    template_name = "account/login.html"
    success_message = "You were successfully logged in."


class LogoutConfirmView(generic.TemplateView):
    template_name = "account/logout_confirm.html"


class CustomLogoutView(views.LogoutView):
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        messages.add_message(
            request, messages.INFO, "You were successfully logged out."
        )
        return response


class LogoutDoneView(generic.TemplateView):
    template_name = "account/logout_done.html"


class SignupView(SuccessMessageMixin, generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("users:email_verify_sent")
    template_name = "account/signup.html"
    success_message = "User registration successful. Verification email sent."

    def form_valid(self, form):
        user = form.save()
        # Set some values to trigger the send_email method.
        opts = {
            "use_https": self.request.is_secure(),
            "from_email": getattr(settings, "DEFAULT_FROM_EMAIL"),
        }
        send_email_verification(user, **opts)

        return super().form_valid(form)


class CustomPasswordChangeView(SuccessMessageMixin, views.PasswordChangeView):
    template_name = "account/password_change.html"
    success_message = "Your password was changed successfully."


class CustomPasswordChangeDoneView(views.PasswordChangeDoneView):
    template_name = "account/password_change_done.html"


class CustomPasswordResetView(SuccessMessageMixin, views.PasswordResetView):
    template_name = "account/password_reset_form.html"
    success_message = "A password reset link was sent to your email."


class CustomPasswordResetDoneView(views.PasswordResetDoneView):
    template_name = "account/password_reset_done.html"


class CustomPasswordResetConfirmView(
    SuccessMessageMixin, views.PasswordResetConfirmView
):
    template_name = "account/password_reset_confirm.html"
    success_message = "Your password was reset successfully. Please log in."


class CustomPasswordResetCompleteView(views.PasswordResetCompleteView):
    template_name = "account/password_reset_complete.html"


class EmailVerifyView(generic.FormView):
    form_class = EmailVerifyForm
    template_name = "account/email_verify.html"
    success_url = reverse_lazy("users:email_verify_sent")
    success_message = "Verification email requested."

    def form_valid(self, form):
        opts = {
            "use_https": self.request.is_secure(),
            "from_email": getattr(settings, "DEFAULT_FROM_EMAIL"),
        }
        form.save(**opts)
        return super().form_valid(form)


class EmailVerifySentView(generic.TemplateView):
    template_name = "account/email_verify_sent.html"


@method_decorator(sensitive_post_parameters(), name="dispatch")
class EmailVerifyConfirmView(generic.FormView):
    form_class = EmailVerifyConfirmForm
    template_name = "account/email_verify_confirm.html"
    success_url = reverse_lazy("users:email_verify_done")
    success_message = "Email verification successful."

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        valid_user = self.check_validity(email=email)
        if valid_user is None:
            return self.render_to_response(self.get_context_data(email=email))
        valid_user.is_active = True
        valid_user.save()
        return super().form_valid(form)

    def check_validity(self, email=None):
        uidb64 = self.kwargs.get("uidb64")
        token = self.kwargs.get("token")

        try:
            uid = force_str(uid_decoder(uidb64))
            opts = {"pk": uid}
            if email is not None:
                opts["email"] = email
            user = CustomUser.objects.get(**opts)
            if not email_verification_token.check_token(user, token) or user.is_active:
                user = None
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        return user

    def get_context_data(self, **kwargs):
        email = kwargs.pop("email", None)
        context = super().get_context_data(**kwargs)

        valid = self.check_validity(email)

        if valid is not None:
            context["validlink"] = True
        else:
            context.update(
                {
                    "form": None,
                    "title": "Email verification unsuccessful.",
                    "validlink": False,
                }
            )
        return context


class EmailVerifyDoneView(generic.TemplateView):
    template_name = "account/email_verify_done.html"


class UserProfileView(SelfOrAdminRequiredMixin, generic.DetailView):
    model = CustomUser
    context_object_name = "profile_user"
    template_name = "account/user/profile.html"
    slug_field = "handle"
    slug_url_kwarg = "handle"


class UpdateHandleView(
    SelfOrAdminRequiredMixin, SuccessMessageMixin, generic.UpdateView
):
    model = CustomUser
    context_object_name = "profile_user"
    template_name = "account/user/update_handle.html"
    slug_field = "handle"
    slug_url_kwarg = "handle"
    success_message = "Your handle was updated successfully."
    fields = ["handle"]

    def form_invalid(self, form):
        taken_msg = "This handle is already taken."
        messages.add_message(self.request, messages.WARNING, taken_msg)
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy("users:profile", kwargs={"handle": self.object.handle})
