from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from accounts.models import Profile
from comments.models import Comment
from comments.serializers import CommentSerializers
from posts.models import Post

COMMENT_URL = reverse("comments:comment-list")


def sample_comment(user, **params) -> Comment:
    defaults = {
        "text": "Test comment",
    }
    defaults.update(params)
    profile, _ = Profile.objects.get_or_create(user=user)
    post = Post.objects.create(content="Test post", author=profile)
    comment, created = Comment.objects.get_or_create(user=user, post=post, defaults=defaults)
    if not created:
        for key, value in defaults.items():
            setattr(comment, key, value)
        comment.save()
    return comment


def detail_url(comment_id):
    return reverse("comments:comment-detail", args=(comment_id,))


class PublicCommentApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(email="anonymous@test.com", password="test1234")

    def test_list_comments(self):
        sample_comment(user=self.user)
        res = self.client.get(COMMENT_URL)

        comments = Comment.objects.all()
        serializer = CommentSerializers(comments, many=True, context={"request": res.wsgi_request})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


class PrivateProfileApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="test12345"
        )
        self.client.force_authenticate(self.user)
        profile, _ = Profile.objects.get_or_create(user=self.user)
        profile.save()
        self.post = Post.objects.create(content="Test post content", author=profile)
        self.comment = Comment.objects.create(
            user=self.user, post=self.post, text="First test comment"
        )

    def test_retrieve_comment_detail(self):
        comment = sample_comment(user=self.user)

        url = detail_url(comment.id)

        res = self.client.get(url)

        serializer = CommentSerializers(comment, context={"request": res.wsgi_request})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_comment(self):

        profile, _ = Profile.objects.get_or_create(user=self.user)
        profile.save()

        self.post, _ = Post.objects.get_or_create(content="Test post", author=profile)

        payload = {
            "post_id": self.post.id,
            "text": "New comment",
        }

        res = self.client.post(COMMENT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        comment = Comment.objects.get(text=payload["text"])

        self.assertEqual(comment.user, self.user)

    def test_update_comment(self):
        payload = {"post_id": self.post.id, "text": "Update text comment"}

        url = detail_url(self.comment.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.comment.refresh_from_db()

        self.assertEqual(self.comment.text, payload["text"])

    def test_delete_comment(self):

        url = detail_url(self.comment.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())
