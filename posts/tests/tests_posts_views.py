from datetime import timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.timezone import now
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from accounts.models import Profile
from posts.models import Hashtag, Post
from posts.serializers import PostListSerializers, PostRetrieveSerializer

POSTS_URL = reverse("posts:post-list")


def detail_url(post_id):
    return reverse("posts:post-detail", args=(post_id,))


class PublicPostApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(POSTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class PrivatePostApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user1 = get_user_model().objects.create_user(
            username="user1",
            email="test1@test.com",
            password="test12345"
        )

        self.client.force_authenticate(self.user1)
        self.profile1, _ = Profile.objects.get_or_create(user=self.user1)

        self.hashtag = Hashtag.objects.create(name="testhashtag", author=self.profile1)
        self.post = Post.objects.create(content="Test post #testhashtag", author=self.profile1, is_published=True)
        self.post.hashtags.add(self.hashtag)

    def test_list_posts(self):
        res = self.client.get(POSTS_URL)

        post = Post.objects.all()
        serializer = PostListSerializers(post, many=True, context={"request": res.wsgi_request})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_post_detail(self):
        url = detail_url(self.post.id)
        res = self.client.get(url)

        serializer = PostRetrieveSerializer(self.post, context={"request": res.wsgi_request})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.data["content"], self.post.content)
        self.assertEqual(res.data["author_name"], self.user1.username)

    def test_create_post(self):
        payload = {
            "content": "New test post #newhashtag",
        }

        res = self.client.post(POSTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        post = Post.objects.get(content=payload["content"])

        self.assertEqual(post.author, self.profile1)
        self.assertEqual(post.hashtags.filter(name="newhashtag").exists(), True)

    def test_update_post(self):
        payload = {"content": "Update post #updatedhashtag"}

        url = detail_url(self.post.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.post.refresh_from_db()
        self.assertEqual(self.post.content, "Update post #updatedhashtag")
        self.assertEqual(self.post.hashtags.filter(name="updatedhashtag").exists(), True)

    def test_delete_post(self):
        url = detail_url(self.post.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())

    def test_by_hashtag(self):
        res = self.client.get(POSTS_URL, {"hashtag": "testhashtag"})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["content"], self.post.content)

    def test_schedule_post(self):
        future_time = (now() + timedelta(days=1)).isoformat()
        payload = {"content": "Scheduled post", "publish_at": future_time}

        url = reverse("posts:post-schedule")
        res = self.client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("message", res.data)
        self.assertTrue("Post scheduled for" in res.data["message"])

        post = Post.objects.get(content="Scheduled post")
        self.assertEqual(post.publish_at.isoformat(), future_time)
        self.assertFalse(post.is_published)
