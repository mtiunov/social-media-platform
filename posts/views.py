from django.utils import timezone
from django.utils.dateparse import parse_datetime
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter, OpenApiExample
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from accounts.models import Profile
from interactions.models import Subscription
from posts.models import Post, Hashtag
from posts.serializers import HashtagSerializer, PostListSerializers, PostSerializers, PostRetrieveSerializer
from posts.filters import PostFilter
from django_celery_beat.models import PeriodicTask, ClockedSchedule
import json


@extend_schema_view(
    list=extend_schema(
        summary="List Visible Posts",
        description="Get a list of posts visible to the authenticated user (their posts + posts of users they follow) "
                    "or published posts (for anonymous users). Results can be filtered by "
                    "hashtag name (query parameter 'hashtags').",
        parameters=[
            OpenApiParameter(
                name="hashtags",
                type=OpenApiTypes.STR,
                location="query",
                description="Filter posts by hashtag name (case-insensitive, exact match).",
                required=False,
            ),
        ],
        responses={200: PostListSerializers(many=True)},
        tags=["Posts"],
    ),
    create=extend_schema(
        summary="Create New Post for Immediate Publication",
        description="Create a new post for the authenticated user for immediate publication. "
                    "Hashtags will be automatically extracted from the content.",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The content of the post. Hashtags (#tag) within the content will "
                                       "be extracted automatically upon saving.",
                        "required": True,
                    },
                    "image": {
                        "type": "string",
                        "format": "binary",
                        "description": "An optional image file to attach to the post.",
                        "required": False,
                    },
                },
                "required": ["content"],
            }
        },
        responses={
            # Відповідь 201 Created: створений об'єкт PostSerializers
            201: PostSerializers,
            400: {
                "description": "Invalid input.",
                "type": "object",
                "properties": {
                    "content": {"type": "array", "items": {"type": "string"}},
                    "image": {"type": "array", "items": {"type": "string"}},
                    "non_field_errors": {"type": "array", "items": {"type": "string"}},
                }
            },
            401: {"description": "Authentication credentials were not provided."},
        },
        tags=["Posts"],
        examples=[
            OpenApiExample(
                "Create Post with Content and Image",
                value={"content": "My first post #awesome #django"},
                request_only=True,
            )
        ]
    ),
    retrieve=extend_schema(
        summary="Get Specific Post",
        description="Retrieve details of a specific post by its ID. Visibility depends on "
                    "authentication and publish status/date (as per list endpoint rules).",
        responses={
            200: PostRetrieveSerializer,
            404: {"description": "Post not found or not visible."},
        },
        tags=["Posts"],
    ),
    update=extend_schema(
        summary="Update Post (PUT)",
        description="Update a post by its ID. Only the author can update their post. "
                    "Hashtags will be re-extracted from the updated content.",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The updated content of the post. Hashtags (#tag) within the content will "
                                       "be re-extracted automatically.",
                        "required": True,
                    },
                    "image": {
                        "type": "string",
                        "format": "binary",
                        "description": "An updated image file. Send null or omit field to clear the image.",
                        "required": False,
                        "x-nullable": True
                    },
                },
                "required": ["content"],
            }
        },
        responses={
            200: PostSerializers,
            400: {
                "description": "Invalid input.",
                "type": "object",
                "properties": {"content": {"type": "array", "items": {"type": "string"}},
                               "image": {"type": "array", "items": {"type": "string"}}}
            },
            401: {"description": "Authentication credentials were not provided."},
            403: {"description": "You do not have permission to perform this action."},
            404: {"description": "Post not found or not owned."},
        },
        tags=["Posts"],
    ),

    partial_update=extend_schema(
        summary="Partially Update Post (PATCH)",
        description="Partially update a post by its ID. Only the author can update their post. "
                    "Hashtags will be re-extracted from the updated content.",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The updated content of the post. Hashtags (#tag) within the content will "
                                       "be re-extracted automatically.",
                        "required": False,
                    },
                    "image": {
                        "type": "string",
                        "format": "binary",
                        "description": "An updated image file. Send null or omit field to clear the image.",
                        "required": False,
                        'x-nullable': True
                    },
                },
                "required": [],
            }
        },
        responses={
            200: PostSerializers,
            400: {
                "description": "Invalid input.",
                "type": "object",
                "properties": {"content": {"type": "array", "items": {"type": "string"}},
                               "image": {"type": "array", "items": {"type": "string"}}}
            },
            401: {"description": "Authentication credentials were not provided."},
            403: {"description": "You do not have permission to perform this action."},
            404: {"description": "Post not found or not owned."},
        },
        tags=["Posts"],
    ),

    destroy=extend_schema(
        summary="Delete Post",
        description="Delete a post by its ID. Only the author can delete their post.",
        responses={
            204: {"description": "Post deleted successfully (No Content)."},
            401: {"description": "Authentication credentials were not provided."},
            403: {"description": "You do not have permission to perform this action."},
            404: {"description": "Post not found or not owned."},
        },
        tags=["Posts"],
    ),

    by_hashtag=extend_schema(
        summary="List Posts by Hashtag",
        description="Get a list of posts associated with a specific hashtag. "
                    "Post visibility rules (as per list endpoint) apply.",
        parameters=[
            OpenApiParameter(
                name="hashtag",
                type=OpenApiTypes.STR,
                location="query",
                description="The name of the hashtag (without the # symbol) to filter posts by.",
                required=True,
            )
        ],
        methods=["get"],
        responses={
            200: PostSerializers(many=True),
            400: {"description": "Hashtag is required.", "type": "object", "properties": {"error": {"type": "string"}}},
            404: {"description": "No visible posts found for this hashtag.", "type": "object",
                  "properties": {"message": {"type": "string"}}},
        },
        tags=["Posts"],
    ),

    schedule=extend_schema(
        summary="Schedule Post Publication",
        description="Schedule a post to be created and published automatically at a future date and time. "
                    "The post will be initially unpublished.",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The content of the scheduled post. "
                                       "Hashtags (#tag) will be extracted upon publication.",
                        "required": True,
                    },
                    "publish_at": {
                        "type": "string",
                        "format": "date-time",
                        "description": "The date and time to publish the post "
                                       "(ISO 8601 format, e.g., 2023-10-27T10:00:00Z). Must be in the future.",
                        "required": True,
                    },
                    "image": {
                        "type": "string",
                        "format": "binary",
                        "description": "An optional image file to attach to the scheduled post.",
                        "required": False,
                    },
                },
                "required": ["content", "publish_at"],
            }
        },
        methods=["post"],
        responses={
            201: { "description": "Post scheduled successfully.", "type": "object", "properties": {"message": {"type": "string"}} },
            400: {
                "description": "Invalid input.",
                "type": "object",
                "properties": {
                    "content": {"type": "array", "items": {"type": "string"}},
                    "publish_at": {"type": "array", "items": {"type": "string"}},
                    "image": {"type": "array", "items": {"type": "string"}},
                    "error": {"type": "string"}
                }
            },
            401: {"description": "Authentication credentials were not provided."},
        },
        tags=["Posts"],
    ),
)
class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostListSerializers

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_filterset_class(self):
        """
        Returns the filterset class to use for the current action.
        Only used for the 'list' action to enable automatic filtering by hashtag.
        """
        if self.action == "list":
            return PostFilter
        return None

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializers
        elif self.action == "retrieve":
            return PostRetrieveSerializer
        return PostSerializers

    def get_queryset(self):
        queryset = Post.objects.select_related("author", "author__user").prefetch_related("hashtags")

        if self.request.user.is_authenticated:
            user_profile = Profile.objects.select_related("user").get(user=self.request.user)
            following_profiles = Subscription.objects.filter(follower=self.request.user
                                                             ).values_list("following", flat=True)
            return queryset.filter(
                author__in=[user_profile] + list(following_profiles)
            ).prefetch_related("hashtags")
        else:
            return queryset.filter(
                is_published=True,
                publish_at__lte=timezone.now()
            ).prefetch_related("hashtags")

    def perform_create(self, serializer):
        user_profile = Profile.objects.get(user=self.request.user)
        post = serializer.save(author=user_profile, is_published=True)
        post.extract_hashtags(post_author=user_profile)

    def perform_update(self, serializer):
        post = serializer.save()
        post.extract_hashtags(post_author=post.author)

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

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
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


@extend_schema_view(
    list=extend_schema(
        summary="List Hashtags",
        description="Get a list of all hashtags.",
        responses={200: HashtagSerializer(many=True)},
        tags=["Hashtags"]
    ),
    retrieve=extend_schema(
        summary="Get Specific Hashtags",
        description="Retrieve details of a specific hashtag by its ID.",
        responses={
            200: HashtagSerializer,
            404: {"description": "Hashtag not found or not visible."},
        },
        tags=["Hashtags"],
    ),
    destroy=extend_schema(
        summary="Delete Hashtag",
        description="Delete a hashtag by its ID. Only the author can delete their Hashtags.",
        responses={
            204: {"description": "Hashtag deleted successfully (No Content)."},
            401: {"description": "Authentication credentials were not provided."},
            403: {"description": "You do not have permission to perform this action."},
            404: {"description": "Hashtag not found."},
        },
        tags=["Hashtags"],
    ),
)
class HashtagViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Hashtag.objects.all()
    serializer_class = HashtagSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        """
        Gets the Hashtag object by PK. Ownership checking is done in the destroy method.
        """
        queryset = self.get_queryset()

        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        if lookup_url_kwarg not in self.kwargs:
            raise AttributeError("Lookup URL keyword argument not provided.")

        obj = get_object_or_404(queryset, **self.kwargs)
        return obj

    def destroy(self, request, *args, **kwargs):
        """
        Delete a hashtag. Only the hashtag owner is allowed.
        """
        instance = self.get_object()

        if instance.author is None or instance.author.user != request.user:
            raise PermissionDenied("You do not have permission to perform this action.")

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
