from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return str(user.is_active) + str(user.pk) + str(timestamp)


email_verification_token = EmailVerificationTokenGenerator()


def send_email_verification(user, *args, **kwargs):
    """Sends an account verification email to the user.

    Sent after signup automatically or requested manually via EmailVerify views.
    """
    use_https = kwargs.pop("use_https", False)
    subject = "Activate Your Account"
    message = render_to_string(
        "account/email/verification.html",
        {
            "site": Site.objects.get_current(),
            "user": user,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": email_verification_token.make_token(user),
            "protocol": "https" if use_https else "http",
        },
    )
    user.email_user(subject, message, **kwargs)
