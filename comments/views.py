from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiExample
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny

from comments.models import Comment
from comments.serializers import CommentSerializers


@extend_schema_view(
    list=extend_schema(
        summary="Comments List",
        description="Get a list Comment.",
        tags=["Comments"],
    ),
    retrieve=extend_schema(
        summary="Comments detail",
        description="Get a detailed information about a comment by its ID.",
        tags=["Comments"],
    ),
    create=extend_schema(
        summary="Create Comments",
        description="Creates a new comment, tied to the current authenticated user.",
        request=CommentSerializers,
        responses={
            201: CommentSerializers,
            400: OpenApiExample(
                "Bad Request Example",
                value={"post_id": ["This field is required."]},
                response_only=True,
                status_codes=["400"]
            )
        },
        examples=[
            OpenApiExample(
                "Example comment creation",
                summary="Example comment creation",
                description="Send the text of the comment and the post ID to which it refers.",
                value={
                    "post_id": 2,
                    "text": "I create a new comment.",
                },
                request_only=True,
                status_codes=["201"]
            )
        ],
        tags=["Comments"],
    ),
    update=extend_schema(
        summary="Update Comment",
        description="Update existing comment. Available only to the comment owner.",
        request=CommentSerializers,
        responses={200: CommentSerializers},
        examples=[
            OpenApiExample(
                name="Example comment update",
                value={
                    "post_id": 2,
                    "text": "Comment updated",
                },
                request_only=True,
            )
        ],
        tags=["Comments"],
    ),
    partial_update=extend_schema(
        summary="Partial update Comment",
        description="Partially update comment (PATCH). Only available to the comment owner.",
        request=CommentSerializers,
        responses={200: CommentSerializers},
        examples=[
            OpenApiExample(
                name="Partial update",
                value={
                    "post_id": 2,
                    "text": "Comment partial updated",
                },
                request_only=True,
            )
        ],
        tags=["Comments"],
    ),
    destroy=extend_schema(
        summary="Destroy comment",
        description="Delete comment. Available only to the comment owner.",
        responses={204: None},
        tags=["Comments"],
    ),
)
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related("user", "post")
    serializer_class = CommentSerializers

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated()]
        return [AllowAny()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
