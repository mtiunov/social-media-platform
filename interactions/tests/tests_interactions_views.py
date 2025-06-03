from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from accounts.models import Profile
from interactions.models import LikeUnlikeDislike
from interactions.serializers import LikeUnlikeDislikeSerializers
from posts.models import Post

LIKEUNLIKEDISLIKE_URL = reverse("interactions:like-list")


def detail_url(like_id):
    return reverse("interactions:like-detail", args=(like_id,))


class PublicInteractionApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(LIKEUNLIKEDISLIKE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateInteractionApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="test12345"
        )
        self.client.force_authenticate(self.user)
        self.profile, _ = Profile.objects.get_or_create(user=self.user)
        self.post, _ = Post.objects.get_or_create(content="Test post", author=self.profile)

    def test_list_interactions(self):

        res = self.client.get(LIKEUNLIKEDISLIKE_URL)

        likeunlikedislike = LikeUnlikeDislike.objects.all()
        serializer = LikeUnlikeDislikeSerializers(likeunlikedislike, many=True, context={"request": res.wsgi_request})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_interaction_detail(self):
        interaction = LikeUnlikeDislike.objects.create(user=self.profile, post=self.post, value="like")
        url = detail_url(interaction.id)

        res = self.client.get(url)

        serializer = LikeUnlikeDislikeSerializers(interaction, context={"request": res.wsgi_request})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_interaction(self):
        payload = {
            "post_id": self.post.id,
            "value": "like",
        }

        res = self.client.post(LIKEUNLIKEDISLIKE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        interaction = LikeUnlikeDislike.objects.get(user=self.profile, post=self.post)

        self.assertEqual(interaction.value, payload["value"])

    def test_create_duplicate_interaction_fails(self):
        LikeUnlikeDislike.objects.create(user=self.profile, post=self.post, value="like")

        payload = {
            "post_id": self.post.id,
            "value": "dislike",
        }

        res = self.client.post(LIKEUNLIKEDISLIKE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_interaction(self):
        interaction = LikeUnlikeDislike.objects.create(user=self.profile, post=self.post, value="like")
        payload = {"value": "dislike"}

        url = detail_url(interaction.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        interaction.refresh_from_db()

        self.assertEqual(interaction.value, "dislike")

    def test_delete_interaction(self):
        interaction = LikeUnlikeDislike.objects.create(user=self.profile, post=self.post, value="like")

        url = detail_url(interaction.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(LikeUnlikeDislike.objects.filter(id=interaction.id).exists())
