from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from accounts.models import Profile
from posts.models import Hashtag, Post
from posts.serializers import HashtagSerializer

HASHTAG_URL = reverse("posts:hashtag-list")


def detail_url(hashtag_id):
    return reverse("posts:hashtag-detail", args=(hashtag_id,))


class PublicHashtagApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(HASHTAG_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateHashtagApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user1 = get_user_model().objects.create_user(
            username="user1",
            email="test1@test.com",
            password="test12345"
        )

        self.client.force_authenticate(self.user1)
        self.profile1, _ = Profile.objects.get_or_create(user=self.user1)

        self.hashtag1 = Hashtag.objects.create(name="testhashtag", author=self.profile1)
        self.hashtag2 = Hashtag.objects.create(name="anotherhashtag", author=self.profile1)

    def test_list_hashtag(self):
        hashtags = Hashtag.objects.all()

        res = self.client.get(HASHTAG_URL)
        serializer = HashtagSerializer(hashtags, many=True, context={"request": res.wsgi_request})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_hashtag_detail(self):
        post = Post.objects.create(content="Test post", author=self.profile1)
        hashtag = Hashtag.objects.create(name="pryvit")
        post.hashtags.add(hashtag)

        url = detail_url(hashtag.id)
        res = self.client.get(url)

        serializer = HashtagSerializer(hashtag, context={"request": res.wsgi_request})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_delete_post(self):
        url = detail_url(self.hashtag1.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Hashtag.objects.filter(id=self.hashtag1.id).exists())
