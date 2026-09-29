from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework.test import APIClient


User = get_user_model()


class AccountTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            email="accounttest@example.com",
            username="accounttest",
            password="TestPassword123",
        )

    def test_user_can_signup(self):
        response = self.client.post(
            "/api/auth/signup/",
            {
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "NewPassword123",
                "password2": "NewPassword123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        self.assertTrue(
            User.objects.filter(
                email="newuser@example.com"
            ).exists()
        )

    def test_password_is_hashed(self):
        response = self.client.post(
            "/api/auth/signup/",
            {
                "email": "hashed@example.com",
                "username": "hasheduser",
                "password": "SecurePassword123",
                "password2": "SecurePassword123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        user = User.objects.get(
            email="hashed@example.com"
        )

        self.assertNotEqual(
            user.password,
            "SecurePassword123",
        )

        self.assertTrue(
            user.check_password(
                "SecurePassword123"
            )
        )

    def test_signup_rejects_mismatched_passwords(self):
        response = self.client.post(
            "/api/auth/signup/",
            {
                "email": "mismatch@example.com",
                "username": "mismatchuser",
                "password": "Password123",
                "password2": "DifferentPassword123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "password",
            response.data,
        )

    def test_signup_rejects_duplicate_email(self):
        response = self.client.post(
            "/api/auth/signup/",
            {
                "email": self.user.email,
                "username": "anotherusername",
                "password": "Password123",
                "password2": "Password123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "email",
            response.data,
        )

    def test_signup_rejects_short_password(self):
        response = self.client.post(
            "/api/auth/signup/",
            {
                "email": "short@example.com",
                "username": "shortuser",
                "password": "123",
                "password2": "123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "password",
            response.data,
        )

    def test_user_can_login(self):
        response = self.client.post(
            "/api/auth/login/",
            {
                "email": "accounttest@example.com",
                "password": "TestPassword123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIn(
            "access",
            response.data,
        )

        self.assertIn(
            "refresh",
            response.data,
        )

    def test_login_rejects_invalid_password(self):
        response = self.client.post(
            "/api/auth/login/",
            {
                "email": "accounttest@example.com",
                "password": "WrongPassword123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_unauthenticated_user_cannot_access_me(self):
        response = self.client.get(
            "/api/auth/me/"
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_authenticated_user_can_access_me(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            "/api/auth/me/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.data["id"],
            self.user.id,
        )

        self.assertEqual(
            response.data["email"],
            self.user.email,
        )

        self.assertEqual(
            response.data["username"],
            self.user.username,
        )

    def test_refresh_token_returns_new_access_token(self):
        login_response = self.client.post(
            "/api/auth/login/",
            {
                "email": "accounttest@example.com",
                "password": "TestPassword123",
            },
            format="json",
        )

        self.assertEqual(
            login_response.status_code,
            200,
        )

        refresh_token = login_response.data["refresh"]

        response = self.client.post(
            "/api/auth/refresh/",
            {
                "refresh": refresh_token,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIn(
            "access",
            response.data,
        )

    def test_login_rejects_unknown_user(self):
        response = self.client.post(
            "/api/auth/login/",
            {
                "email": "doesnotexist@example.com",
                "password": "TestPassword123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_signup_requires_email(self):
        response = self.client.post(
            "/api/auth/signup/",
            {
                "username": "noemailuser",
                "password": "Password123",
                "password2": "Password123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "email",
            response.data,
        )

    def test_signup_requires_username(self):
        response = self.client.post(
            "/api/auth/signup/",
            {
                "email": "nousername@example.com",
                "password": "Password123",
                "password2": "Password123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "username",
            response.data,
        )