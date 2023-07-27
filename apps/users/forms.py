from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.core.exceptions import ValidationError

from .tokens import send_email_verification

CustomUser = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("email",)

    def save(self, commit=True):
        user = super().save(commit=False)
        try:
            user.full_clean()
        except ValidationError:
            # handle is taken, make unique
            user.make_handle_unique()
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ("email",)


class EmailVerifyForm(forms.Form):
    email = forms.EmailField()

    def save(self, *args, **kwargs):
        email = self.cleaned_data["email"]
        try:
            user = CustomUser.objects.get(email=email)
            if user.is_active:
                user = None
        except CustomUser.DoesNotExist:
            user = None

        if user is not None:
            send_email_verification(user, **kwargs)


class EmailVerifyConfirmForm(forms.Form):
    email = forms.EmailField()
