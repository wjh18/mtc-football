from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import serializers

from ..utils import validate_user_password


class TestValidateUserPassword(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(email="user@example.com", password="foo")

    def test_weak_pw_raises_validation_error(self):
        with self.assertRaises(serializers.ValidationError):
            validate_user_password(self.user, "test", "password")

    def test_strong_pw_does_not_raise_validation_error(self):
        validate_user_password(self.user, "v3rystr0ng174", "password")
