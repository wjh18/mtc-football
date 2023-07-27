from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import serializers
from rest_framework.test import APIRequestFactory

from ..serializers import (
    LoginSerializer,
    PasswordChangeSerializer,
    RegisterUserSerializer,
)


class RegisterUserSerializerTest(TestCase):
    def setUp(self):
        self.User = get_user_model()

    def test_valid_data_creates_user(self):
        data = {
            "email": "user@example.com",
            "password": "strongpass123",
            "confirm_password": "strongpass123",
        }
        # Request is needed during email verif.
        factory = APIRequestFactory()
        request = factory.post("/api/accounts/signup/", data, format="json")

        serializer = RegisterUserSerializer(data=data, context={"request": request})
        is_valid = serializer.is_valid()
        self.assertTrue(is_valid)
        self.assertCountEqual(serializer.validated_data.keys(), ["email", "password"])

        serializer.create(serializer.validated_data)
        user_exists = self.User.objects.filter(email="user@example.com").exists()
        self.assertTrue(user_exists)

    def test_mismatched_passwords_are_invalid(self):
        data = {
            "email": "user@example.com",
            "password": "strongpass123",
            "confirm_password": "strongpass789",
        }
        serializer = RegisterUserSerializer(data=data)
        is_valid = serializer.is_valid()
        self.assertFalse(is_valid)
        for field in ("password", "confirm_password"):
            self.assertEqual(serializer.errors[field][0], "Passwords must match.")

        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_weak_password_is_invalid(self):
        data = {
            "email": "user@example.com",
            "password": "foo",
            "confirm_password": "foo",
        }
        serializer = RegisterUserSerializer(data=data)
        is_valid = serializer.is_valid()
        self.assertFalse(is_valid)
        self.assertEqual(
            serializer.errors["password"][0],
            "This password is too short. It must contain at least 8 characters.",
        )

        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_email_already_in_use_is_invalid(self):
        self.User.objects.create_user(email="user@example.com", password="foo")
        data = {
            "email": "user@example.com",
            "password": "strongpass123",
            "confirm_password": "strongpass123",
        }
        serializer = RegisterUserSerializer(data=data)
        is_valid = serializer.is_valid()
        self.assertFalse(is_valid)
        self.assertEqual(
            serializer.errors["email"][0],
            "user with this email address already exists.",
        )

        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_email_missing_is_invalid(self):
        data = {"password": "strongpass123", "confirm_password": "strongpass123"}
        serializer = RegisterUserSerializer(data=data)
        is_valid = serializer.is_valid()
        self.assertFalse(is_valid)
        self.assertEqual(serializer.errors["email"][0], "This field is required.")

        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_password_missing_is_invalid(self):
        data = {"email": "user@example.com", "confirm_password": "strongpass123"}
        serializer = RegisterUserSerializer(data=data)
        is_valid = serializer.is_valid()
        self.assertFalse(is_valid)
        self.assertEqual(serializer.errors["password"][0], "This field is required.")

        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_confirm_password_missing_is_invalid(self):
        data = {
            "email": "user@example.com",
            "password": "strongpass123",
        }
        serializer = RegisterUserSerializer(data=data)
        is_valid = serializer.is_valid()
        self.assertFalse(is_valid)
        self.assertEqual(
            serializer.errors["confirm_password"][0], "This field is required."
        )

        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)


class LoginSerializerTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.email = "user@example.com"
        self.password = "foo"
        self.user = User.objects.create_user(
            email=self.email, password=self.password, is_active=True
        )
        factory = APIRequestFactory()
        self.request = factory.get("/api/accounts/login/")

    def test_email_and_password_are_valid(self):
        serializer = LoginSerializer(
            data={"email": self.email, "password": self.password},
            context={"request": self.request},
        )
        is_valid = serializer.is_valid()
        self.assertTrue(is_valid)
        # self.assertCountEqual(serializer.data.keys(), ["email", "password"])

    def test_email_missing_is_invalid(self):
        serializer = LoginSerializer(
            data={"password": self.password}, context={"request": self.request}
        )
        is_valid = serializer.is_valid()
        self.assertFalse(is_valid)
        self.assertCountEqual(serializer.errors.keys(), ["email"])
        self.assertEqual(serializer.errors["email"][0].code, "required")

        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_password_missing_is_invalid(self):
        serializer = LoginSerializer(
            data={"email": self.email}, context={"request": self.request}
        )
        is_valid = serializer.is_valid()
        self.assertFalse(is_valid)
        self.assertCountEqual(serializer.errors.keys(), ["password"])
        self.assertEqual(serializer.errors["password"][0].code, "required")

        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_no_data_is_invalid(self):
        serializer = LoginSerializer(data={}, context={"request": self.request})
        is_valid = serializer.is_valid()
        self.assertFalse(is_valid)
        self.assertCountEqual(serializer.errors.keys(), ["email", "password"])
        self.assertEqual(serializer.errors["email"][0].code, "required")
        self.assertEqual(serializer.errors["password"][0].code, "required")

        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)


class PasswordChangeSerializerTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.password = "foo"
        self.user = User.objects.create_user(
            email="user@example.com", password=self.password
        )

    def test_password_not_supplied_raises_validation_error(self):
        data = {"new_password": "fj2fjh209jf3", "confirm_new_password": "fj2fjh209jf3"}
        serializer = PasswordChangeSerializer(data=data, context={"user": self.user})
        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_new_pw_not_supplied_raises_validation_error(self):
        data = {"password": self.password, "confirm_new_password": "fj2fjh209jf3"}
        serializer = PasswordChangeSerializer(data=data, context={"user": self.user})
        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_confirm_new_pw_not_supplied_raises_validation_error(self):
        data = {"password": self.password, "new_password": "fj2fjh209jf3"}
        serializer = PasswordChangeSerializer(data=data, context={"user": self.user})
        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_invalid_old_pw_raises_validation_error(self):
        data = {
            "password": "wrong",
            "new_password": "fj2fjh209jf3",
            "confirm_new_password": "fj2fjh209jf3",
        }
        serializer = PasswordChangeSerializer(data=data, context={"user": self.user})
        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_non_matching_new_pw_raises_validation_error(self):
        data = {
            "password": self.password,
            "new_password": "y3llowr3d849",
            "confirm_new_password": "gr3enblu3849",
        }
        serializer = PasswordChangeSerializer(data=data, context={"user": self.user})
        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_weak_new_pw_raises_validation_error(self):
        data = {
            "password": self.password,
            "new_password": "weak",
            "confirm_new_password": "weak",
        }
        serializer = PasswordChangeSerializer(data=data, context={"user": self.user})
        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_valid_data_changes_pw(self):
        new_pw = "fj2fjh209jf3"
        data = {
            "password": self.password,
            "new_password": new_pw,
            "confirm_new_password": new_pw,
        }
        serializer = PasswordChangeSerializer(data=data, context={"user": self.user})
        serializer.is_valid(raise_exception=True)
        self.assertTrue(self.user.check_password(new_pw))
