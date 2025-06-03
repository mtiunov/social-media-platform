from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiExample
from rest_framework import viewsets, exceptions, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from accounts.filters import ProfileFilter
from accounts.models import Profile
from accounts.serializers import ProfileSerializers


@extend_schema_view(
    list=extend_schema(
        summary="Profiles List",
        description="Get a list profiles. Filtering, searching, and sorting are supported.",
        responses={
            200: ProfileSerializers(many=True),
            401: {"description": "Authentication credentials were not provided."},
        },
        tags=["Profiles"],
    ),
    retrieve=extend_schema(
        summary="Profiles detail",
        description="Get a detailed information about a profile by its ID.",
        responses={
            200: ProfileSerializers,
            401: {"description": "Authentication credentials were not provided."},
            404: {"description": "Profile not found."},
        },
        tags=["Profiles"],
    ),
    create=extend_schema(
        summary="Create Profile",
        description="Creates a new profile, tied to the current authenticated user.",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "first_name": {"type": "string", "required": False},
                    "last_name": {"type": "string", "required": False},
                    "birthdate": {
                        "type": "string",
                        "format": "date",
                        "description": "A brief description of your biography.",
                        "required": False
                    },
                    "location": {"type": "string", "required": False},
                    "gender": {
                        "type": "string",
                        "enum": ["Female", "Male", "unknown"],
                        "required": True},
                    "bio": {
                        "type": "string",
                        "description": "A brief description of your biography.",
                        "required": True,
                    },
                    "picture": {
                        "type": "string",
                        "format": "binary",
                        "description": "An optional image file to attach to the profile.",
                        "required": False,
                    },
                },
                "required": ["bio", "gender"],
            }
        },
        responses={
            201: ProfileSerializers,
            400: {
                "description": "Invalid input or Profile already exists for this ",
                "type": "object",
                "properties": {
                    "first_name": {"type": "array", "items": {"type": "string"}},
                    "last_name": {"type": "array", "items": {"type": "string"}},
                    "birthdate": {"type": "array", "items": {"type": "string"}},
                    "location": {"type": "array", "items": {"type": "string"}},
                    "gender": {"type": "array", "items": {"type": "string"}},
                    "picture": {"type": "array", "items": {"type": "string"}},
                    "bio": {"type": "array", "items": {"type": "string"}},
                    "non_field_errors": {"type": "array", "items": {"type": "string"}},
                }
            },
            401: {"description": "Authentication credentials were not provided."},
        },
        tags=["Profiles"],
    ),
    update=extend_schema(
        summary="Update profile",
        description="Update existing profile. Available only to the profile owner.",
        responses={
            200: ProfileSerializers,
            400: {
                "description": "Invalid input.",
                "type": "object",
            },
            401: {"description": "Authentication credentials were not provided."},
            403: {"description": "You do not have permission to update this profile."},
            404: {"description": "Profile not found."},
        },
        tags=["Profiles"],
    ),
    partial_update=extend_schema(
        summary="Partial update profile",
        description="Partially update profile (PATCH). Only available to the profile owner.",
        responses={
            200: ProfileSerializers,
            400: {
                "description": "Invalid input.",
                "type": "object",
            },
            401: {"description": "Authentication credentials were not provided."},
            403: {"description": "You do not have permission to perform this action."},
            404: {"description": "Profile not found."},
        },
        tags=["Profiles"],
    ),
    destroy=extend_schema(
        summary="Destroy profile",
        description="Delete profile. Available only to the profile owner.",
        responses={
            204: {"description": "Profile deleted successfully (No Content)."},
            401: {"description": "Authentication credentials were not provided."},
            403: {"description": "You do not have permission to delete this profile."},
            404: {"description": "Profile not found."},
        },
        tags=["Profiles"],
    ),
    me=extend_schema(
        summary="Get My Profile",
        description="Get the profile of the currently logged in user.",
        responses={
            200: ProfileSerializers,
            401: {"description": "Authentication credentials were not provided."},
            404: {"description": "Profile does not exist for this user."},
        },
        tags=["Profiles"],
        examples=[
            OpenApiExample(
                "Example of a profile response",
                value={
                    "id": 5,
                    "username": "johndoe",
                    "email": "john@example.com",
                    "bio": "Backend developer",
                    "location": "Kyiv",
                    "gender": "male",
                },
                response_only=True,
            )
        ]
    ),
)
class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.select_related("user")
    serializer_class = ProfileSerializers
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter
                       ]
    filterset_class = ProfileFilter
    search_fields = ["username", "first_name", "last_name", "email"]
    ordering_fields = ["username", "email", "location", "gender"]
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        user = self.request.user
        if Profile.objects.filter(user=user).exists():
            raise ValidationError("Profile already exists for this user.")
        serializer.save(user=user)

    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user:
            raise exceptions.PermissionDenied("You do not have permission to update this profile.")
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise exceptions.PermissionDenied("You do not have permission to delete this profile.")
        instance.delete()

    @extend_schema(
        summary="Get my profile",
        description="Get the profile of the currently logged in user.",
        responses={200: ProfileSerializers},
        tags=["Profiles"],
        examples=[
            OpenApiExample(
                "Exemple of a profile response",
                value={
                    "id": 5,
                    "username": "johndoe",
                    "email": "john@example.com",
                    "bio": "Backend developer",
                    "location": "Kyiv",
                    "gender": "male",
                },
                response_only=True,
            )
        ]
    )
    @action(detail=False, methods=["get"])
    def me(self, request):
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            raise Http404("Profile does not exist.")
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
