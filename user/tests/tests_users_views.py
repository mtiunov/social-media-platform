from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


class UserApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@test.com",
            username="testuser",
            password="test12345"
        )
        self.token = Token.objects.create(user=self.user)

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_create_user(self):
        payload = {"email": "newuser@test.com", "password": "newpassword"}

        url = reverse("user:register")
        res = self.client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(get_user_model().objects.filter(email="newuser@test.com").exists())

    def test_login_user(self):
        payload = {"email": "testuser@test.com", "password": "test12345"}

        url = reverse("user:api-login")
        res = self.client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("token", res.data)

    def test_retrieve_user_profile(self):
        url = reverse("user:manage")
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["email"], self.user.email)
        self.assertEqual(res.data["id"], self.user.id)

    def test_update_user_profile(self):
        payload = {"password": "newsecurepassword"}
        url = reverse("user:manage")
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newsecurepassword"))

    def test_logout_user(self):
        url = reverse("user:api-logout")
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["detail"], "Successfully logged out")

        self.assertFalse(Token.objects.filter(user=self.user).exists())
