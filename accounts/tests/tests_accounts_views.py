import datetime
import uuid

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from accounts.models import Profile
from accounts.serializers import ProfileSerializers

PROFILE_URL = reverse("accounts:profile-list")


def detail_url(profile_id):
    return reverse("accounts:profile-detail", args=(profile_id,))


def sample_profile(user, **params) -> Profile:
    defaults = {
        "first_name": "Mihail",
        "last_name": "Shumaher",
        "birthdate": datetime.date(1955, 6, 24),
        "location": "Kyiv",
        "gender": "Male",
        "bio": "Test information for profile",
        "picture": SimpleUploadedFile(
            name="test_image.jpg",
            content=b"file_content_not_really_an_image",
            content_type="image/jpeg"
        ),
    }
    defaults.update(params)
    profile, created = Profile.objects.get_or_create(user=user, defaults=defaults)
    if not created:
        for key, value in defaults.items():
            setattr(profile, key, value)
        profile.save()
    return profile


class PublicProfileApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateProfileApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="test12345"
        )
        self.client.force_authenticate(self.user)

    def test_profiles_list(self):
        sample_profile(user=self.user)

        res = self.client.get(PROFILE_URL)
        profiles = Profile.objects.all()
        serializer = ProfileSerializers(profiles, many=True, context={"request": res.wsgi_request})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_profile_search(self):
        sample_profile(user=self.user, first_name="Alex")
        user2 = get_user_model().objects.create_user(
            email="other@test.com",
            username=f"user_{uuid.uuid4()}",
            password="test123"
        )
        sample_profile(user=user2, first_name="John")

        res = self.client.get(PROFILE_URL, {"search": "Alex"})

        profiles = Profile.objects.filter(first_name__icontains="Alex")
        serializer = ProfileSerializers(profiles, many=True, context={"request": res.wsgi_request})

        self.assertEqual(res.data, serializer.data)

    def test_profile_filter(self):
        sample_profile(user=self.user, location="USA")
        user2 = get_user_model().objects.create_user(
            email="other2@test.com",
            username=f"user_{uuid.uuid4()}",
            password="test1234"
        )
        sample_profile(user=user2, location="Kyiv")

        res = self.client.get(PROFILE_URL, {"location__icontains": "USA"})

        profiles = Profile.objects.filter(location__icontains="USA")
        serializer = ProfileSerializers(profiles, many=True, context={"request": res.wsgi_request})

        self.assertEqual(res.data, serializer.data)

    def test_profile_ordering(self):
        sample_profile(user=self.user, username="b_user")
        user2 = get_user_model().objects.create_user(
            email="other3@test.com",
            username=f"user_{uuid.uuid4()}",
            password="test321"
        )
        sample_profile(user=user2, username="a_user")

        res = self.client.get(PROFILE_URL, {"ordering": "username"})
        profiles = Profile.objects.order_by("username")
        serializer = ProfileSerializers(profiles, many=True, context={"request": res.wsgi_request})

        self.assertEqual(res.data, serializer.data)

    def test_retrieve_profile_detail(self):
        profile = sample_profile(user=self.user)

        url = detail_url(profile.id)

        res = self.client.get(url)

        serializer = ProfileSerializers(profile, context={"request": res.wsgi_request})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_profile(self):
        self.client.force_authenticate(self.user)

        Profile.objects.filter(user=self.user).delete()

        payload = {
            "first_name": "New",
            "last_name": "Profile",
            "birthdate": datetime.date(1955, 6, 24),
            "location": "London",
            "gender": "Male",
            "bio": "Another profile attempt",
            "user": self.user
        }

        res = self.client.post(PROFILE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        profile = Profile.objects.get(user=self.user)

        for key, value in payload.items():
            self.assertEqual(getattr(profile, key), value)

    def test_update_profile(self):
        profile = sample_profile(user=self.user)

        payload = {"first_name": "New Name", "last_name": "Update Last", "gender": "Male"}

        url = detail_url(profile.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        profile.refresh_from_db()

        self.assertEqual(profile.first_name, payload["first_name"])
        self.assertEqual(profile.last_name, payload["last_name"])

    def test_delete_profile(self):
        profile = sample_profile(user=self.user)

        url = detail_url(profile.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_me_profile(self):
        profile = sample_profile(user=self.user)

        url = reverse("accounts:profile-me")
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        serializer = ProfileSerializers(profile, context={"request": res.wsgi_request})

        self.assertEqual(res.data, serializer.data)
