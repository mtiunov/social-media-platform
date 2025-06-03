from django.contrib.auth import get_user_model
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiExample,
)
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from interactions.models import LikeUnlikeDislike, Subscription
from interactions.serializers import (
    LikeUnlikeDislikeSerializers,
    SubscriptionSerializers,
)

User = get_user_model()


@extend_schema_view(
    list=extend_schema(
        summary="List User's Reactions",
        description="Get a list of the authenticated user's reactions, optionally filtered by reaction type.",
        parameters=[
            OpenApiParameter(
                name="value",
                type=OpenApiTypes.STR,
                location="query",
                description="Filter by reaction type.",
                required=False,
                enum=[choice[0] for choice in LikeUnlikeDislike.ReactionChoices.choices],
            )
        ],
        tags=["Interactions LikeUnlikeDislike"],
    ),
    retrieve=extend_schema(
        summary="Get Specific User Reaction",
        description="Retrieve details of a specific reaction belonging to the authenticated user by its ID.",
        responses={
            200: LikeUnlikeDislikeSerializers,
            404: {
                "description": "Reaction not found or not owned by user.",
                "type": "object",
                "properties": {"detail": {"type": "string"}}
            },
        },
        tags=["Interactions LikeUnlikeDislike"],
    ),
    create=extend_schema(
        summary="Create New Reaction for a Post",
        description="Creates a new reaction (like or dislike) for a specific post for the authenticated user. "
                    "Returns an error if a reaction for this post already exists.",
        responses={
            201: LikeUnlikeDislikeSerializers,
            400: {
                "description": "Invalid input or missing data.",
                "type": "object",
                "properties": {
                    "post_id": {"type": "array", "items": {"type": "string"}},
                    "value": {"type": "array", "items": {"type": "string"}},
                    "non_field_errors": {"type": "array", "items": {"type": "string"}},
                    "error": {"type": "string"}
                }
            },
            404: {
                "description": "Post not found.",
                "type": "object",
                "properties": {"error": {"type": "string"}}
            },
            409: {
                "description": "Reaction already exists for this post and user. Use PUT to update.",
                "type": "object",
                "properties": {
                    "non_field_errors": {"type": "array", "items": {"type": "string"}}
                },
                "example": {"non_field_errors": ["The fields user, post must make a unique set."]}
            }
        },
        examples=[
            OpenApiExample(
                name="Create Like on Post",
                value={"post_id": 2, "value": "like"},
                request_only=True,
            ),
            OpenApiExample(
                name="Create Dislike on Post",
                value={"post_id": 5, "value": "dislike"},
                request_only=True,
            ),
        ],
        tags=["Interactions LikeUnlikeDislike"],
    ),
    update=extend_schema(
        summary="Update Reaction Value by ID",
        description="Update the value (like or dislike) of "
                    "an existing reaction belonging to the authenticated user by its ID.",
        responses={
            200: LikeUnlikeDislikeSerializers,
            400: {
                "description": "Invalid input.",
                "type": "object",
                "properties": {"value": {"type": "array", "items": {"type": "string"}}}
            },
            404: {
                "description": "Reaction not found or not owned by user.",
                "type": "object",
                "properties": {"detail": {"type": "string"}}
            },
        },
        tags=["Interactions LikeUnlikeDislike"],
    ),
    destroy=extend_schema(
        summary="Delete Specific User Reaction by ID",
        description="Delete a specific reaction belonging to the authenticated user by its ID.",
        responses={
            204: None,
            404: {
                "description": "Reaction not found or not owned by user.",
                "type": "object",
                "properties": {"detail": {"type": "string"}}
            },
        },
        tags=["Interactions LikeUnlikeDislike"],
    )
)
class LikeUnlikeDislikeViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = LikeUnlikeDislikeSerializers
    permission_classes = (IsAuthenticated,)
    REACTION_VALUES = [choice[0] for choice in LikeUnlikeDislike.ReactionChoices.choices]

    def get_queryset(self):
        user_profile = self.request.user.profile

        queryset = LikeUnlikeDislike.objects.select_related(
            "user__user", "post"
        ).filter(user=user_profile)

        value = self.request.query_params.get("value")
        if value in self.REACTION_VALUES:
            queryset = queryset.filter(value=value)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user.profile)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_profile = request.user.profile
        post = serializer.validated_data["post"]

        if LikeUnlikeDislike.objects.filter(user=user_profile, post=post).exists():
            return Response(
                {"error": "Reaction already exists for this post."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, **self.kwargs)
        return obj


@extend_schema_view(
    list=extend_schema(
        summary="List User's Following",
        description="Get a list of users that the authenticated user is following.",
        responses={200: SubscriptionSerializers(many=True)},
        tags=["Subscriptions"],
    ),
    retrieve=extend_schema(
        summary="Get Specific User Subscription",
        description="Retrieve details of a specific subscription belonging to the authenticated user by its ID.",
        responses={
            200: SubscriptionSerializers,
            404: {
                "description": "Subscription not found or not owned by user.",
                "type": "object",
                "properties": {"detail": {"type": "string"}}
            },
        },
        tags=["Subscriptions"],
    ),
    create=extend_schema(
        summary="Create New Subscription (Follow User)",
        description="Creates a new subscription, making the authenticated user a follower of another user. "
                    "Requires the ID or username of the user to follow.",
        responses={
            201: SubscriptionSerializers,
            400: {
                "description": "Invalid input, validation error (cannot subscribe to self, already subscribed), "
                               "or user to follow not found.",
                "type": "object",
                "properties": {
                    "following": {"type": "array", "items": {"type": "string"}},
                    "non_field_errors": {"type": "array", "items": {"type": "string"}},
                    "error": {"type": "string"}
                }
            },
        },
        examples=[
            OpenApiExample(
                name="Follow User by ID",
                value={"following": 5},
                request_only=True,
            ),
        ],
        tags=["Subscriptions"],
    ),
    destroy=extend_schema(
        summary="Delete Specific User Subscription (Unfollow by Subscription ID)",
        description="Delete a specific subscription belonging to the authenticated user by its ID. "
                    "This effectively unfollows the user associated with the subscription ID.",
        responses={
            204: {"description": "Subscription deleted successfully (No Content)."},
            404: {
                "description": "Subscription not found or not owned by user.",
                "type": "object", "properties": {"detail": {"type": "string"}}
            },
        },
        tags=["Subscriptions"],
    ),
    following_list=extend_schema(
        summary="List Who User is Following",
        description="Get a list of subscriptions representing the users that the authenticated user is following.",
        methods=["get"],
        responses={200: SubscriptionSerializers(many=True)},
        tags=["Subscriptions"],
    ),
    followers_list=extend_schema(
        summary="List User's Followers",
        description="Get a list of subscriptions representing the users who are following the authenticated user.",
        methods=["get"],
        responses={200: SubscriptionSerializers(many=True)},
        tags=["Subscriptions"],
    ),
)
class SubscriptionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = SubscriptionSerializers
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Subscription.objects.select_related(
            "follower__profile", "following__profile"
        )
        if self.action == "list":
            return queryset.filter(follower=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(follower=self.request.user)

    def perform_destroy(self, instance):
        return instance.delete()

    def get_object(self):
        queryset = self.get_queryset()
        queryset = queryset.filter(follower=self.request.user)
        obj = get_object_or_404(queryset, **self.kwargs)
        return obj

    @action(detail=False, methods=["get"])
    def following_list(self, request):
        subscription = Subscription.objects.filter(
            follower=request.user
        ).select_related("following__profile", "following__profile__user")
        serializer = self.get_serializer(subscription, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def followers_list(self, request):
        subscription = Subscription.objects.filter(
            following=request.user
        ).select_related("follower__profile", "follower__profile__user")
        serializer = self.get_serializer(subscription, many=True)
        return Response(serializer.data)
