from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from accounts.models import Profile
from interactions.models import Subscription
from posts.models import Post, Hashtag
from posts.serializers import HashtagSerializer, PostListSerializers, PostSerializers, PostRetrieveSerializer
from posts.filters import PostFilter
from django_celery_beat.models import PeriodicTask, ClockedSchedule
import json


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostListSerializers
    filterset_class = PostFilter

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializers
        elif self.action == "retrieve":
            return PostRetrieveSerializer
        return PostSerializers

    def get_queryset(self):
        if self.request.user.is_authenticated:
            user_profile = Profile.objects.select_related("user").get(user=self.request.user)
            following_profiles = Subscription.objects.filter(follower=self.request.user
                                                             ).values_list("following", flat=True)
            return Post.objects.filter(
                author__in=[user_profile] + list(following_profiles)
            ).prefetch_related("hashtags")
        else:
            return Post.objects.filter(
                is_published=True,
                publish_at__lte=timezone.now()
            ).prefetch_related("hashtags")

    def perform_create(self, serializer):
        user_profile = Profile.objects.get(user=self.request.user)
        post = serializer.save(author=user_profile, is_published=True)
        post.extract_hashtags()

    def perform_update(self, serializer):
        post = serializer.save()
        post.extract_hashtags()

    @action(detail=False, methods=["get"])
    def by_hashtag(self, request) -> Response:
        hashtag_name = request.query_params.get("hashtag")
        if not hashtag_name:
            return Response({"error": "Hashtag is required"}, status=status.HTTP_400_BAD_REQUEST)
        hashtag = Hashtag.objects.filter(name=hashtag_name).first()
        if not hashtag:
            return Response({"message": "No posts found for this hashtag"}, status=status.HTTP_404_NOT_FOUND)

        posts = hashtag.posts.all()
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def schedule(self, request):
        content = request.data.get("content")
        publish_at_str = request.data.get("publish_at")
        image = request.data.get("image")

        if not content or not publish_at_str:
            return Response({"error": "Content and publish_at are required."}, status=status.HTTP_400_BAD_REQUEST)

        publish_at = parse_datetime(publish_at_str)
        if publish_at is None:
            return Response({"error": "Invalid publish_at format. Use ISO format (YYYY-MM-DDTHH:MM:SSZ)."},
                            status=status.HTTP_400_BAD_REQUEST)

        if timezone.is_naive(publish_at):
            publish_at = timezone.make_aware(publish_at, timezone.get_default_timezone())

        if publish_at <= timezone.now():
            return Response({"error": "Publish time must be in the future"},
                            status=status.HTTP_400_BAD_REQUEST)

        post = Post.objects.create(
            author=request.user.profile,
            content=content,
            publish_at=publish_at,
            is_published=False,
            image=image
        )

        # Create a ClockedSchedule for a one-time launch
        clocked_schedule, created = ClockedSchedule.objects.get_or_create(
            clocked_time=publish_at
        )

        # Create a PeriodicTask to run our Celery task at a scheduled time
        PeriodicTask.objects.create(
            name=f"publish_post_{post.id}",
            task="posts.tasks.planning_created_posts",
            clocked=clocked_schedule,
            one_off=True,
            kwargs=json.dumps({})
        )

        return Response({"message": f"Post scheduled for {publish_at}."}, status=status.HTTP_201_CREATED)


class HashtagViewSet(viewsets.ModelViewSet):
    queryset = Hashtag.objects.all()
    serializer_class = HashtagSerializer
