from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers


def validate_user_password(user, password, pw_field_name):
    """
    Manually run built-in password validators from serializer validate() method.
    Raise a ValidationError exception if validation doesn't pass.
    """
    try:
        validate_password(password, user=user)
    except ValidationError as e:
        errors = {}
        errors[pw_field_name] = list(e.messages)
        raise serializers.ValidationError(errors)
