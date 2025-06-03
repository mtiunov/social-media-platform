from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from accounts.models import Profile
from interactions.models import Subscription
from interactions.serializers import SubscriptionSerializers

SUBSCRIPTION_URL = reverse("interactions:subscription-list")


def detail_url(subscription_id):
    return reverse("interactions:subscription-detail", args=(subscription_id,))


class PublicSubscriptionApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(SUBSCRIPTION_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateSubscriptionApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user1 = get_user_model().objects.create_user(
            username="user1",
            email="test1@test.com",
            password="test12345"
        )
        self.user2 = get_user_model().objects.create_user(
            username="user2",
            email="test2@test.com",
            password="test1234567"
        )

        self.client.force_authenticate(self.user1)
        self.profile1, _ = Profile.objects.get_or_create(user=self.user1)
        self.profile2, _ = Profile.objects.get_or_create(user=self.user2)

    def test_list_subscription(self):

        res = self.client.get(SUBSCRIPTION_URL)

        subscription = Subscription.objects.all()
        serializer = SubscriptionSerializers(subscription, many=True, context={"request": res.wsgi_request})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_subscription_detail(self):
        subscription = Subscription.objects.create(follower=self.user1, following=self.user2)
        url = detail_url(subscription.id)

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["follower_profile"]["username"], self.user1.username)
        self.assertEqual(res.data["following_profile"]["username"], self.user2.username)

    def test_create_subscription(self):
        payload = {
            "following": self.user2.id,
        }

        res = self.client.post(SUBSCRIPTION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        subscription = Subscription.objects.get(follower=self.user1, following=self.user2)

        self.assertEqual(subscription.follower, self.user1)
        self.assertEqual(subscription.following, self.user2)

    def test_create_duplicate_subscription(self):
        Subscription.objects.create(follower=self.user1, following=self.user2)
        payload = {
            "following": self.user2.id,
        }

        res = self.client.post(SUBSCRIPTION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_subscription(self):
        subscription = Subscription.objects.create(follower=self.user1, following=self.user2)

        url = detail_url(subscription.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Subscription.objects.filter(id=subscription.id).exists())

    def test_following_list(self):
        Subscription.objects.create(follower=self.user1, following=self.user2)

        res = self.client.get(SUBSCRIPTION_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["following_profile"]["username"], self.user2.username)

    def test_followers_list(self):
        Subscription.objects.create(follower=self.user1, following=self.user2)

        res = self.client.get(SUBSCRIPTION_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["follower_profile"]["username"], self.user1.username)
