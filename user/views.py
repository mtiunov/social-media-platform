from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView

from user.serializers import UserSerializer, AuthTokenSerializer


@extend_schema(
    summary="Register New User",
    description="Created a new User account.",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "email": {
                    "type": "string",
                    "format": "email",
                    "description": "Email for New User",
                    "required": True,
                },
                "password": {
                    "type": "string",
                    "format": "password",
                    "description": "User password.",
                    "required": True,
                }
            }
        },
        "required": ["email", "password"],
    },
    responses={
        201: UserSerializer,
        400: {
            "description": "Invalid input data (validation error).",
            "type": "object",
            "properties": {
                "email": {
                    "type": "array", "items": {"type": "sting"},
                    "description": "Validation error for the email."
                },
                "password": {
                    "type": "array", "items": {"type": "string"},
                    "description": "Validation errors for the password field."
                },
                "mom_field_errors": {
                    "type": "array", "items": {"type": "sting"},
                    "description": "Common validation errors."
                }
            }
        }
    },
    tags=["Authentication"],
)
class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


@extend_schema(
    tags=["Authentication"],
)
@extend_schema(
    methods=["GET"],
    summary="Get Auth User Profile",
    description="Get the profile of the currently authenticated user."
)
@extend_schema(
    methods=["PUT"],
    summary="Update Authenticated User Profile",
    description="Update the profile of the currently authenticated user."
)
@extend_schema(
    methods=["PATCH"],
    summary="Partial Update Authenticated User Profile",
    description="Partially updates the profile of the currently authenticated user."
)
class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


@extend_schema(
    summary="Login User",
    description="Get an authentication token for the user based on their username and password.",
    responses={
        200: {
            "description": "Authentication successful, token received.",
            "type": "object",
            "properties": {
                "token": {"type": "string", "description": "Authentication token."}
            }
        },
        400: {
            "description": "Incorrect credentials (login/password).",
            "type": "object",
            "properties": {
                "non_field_errors": {
                    "type": "string",
                    "items": {"type": "string"},
                    "description": "Invalid credentials error."
                }
            }
        }
    },
    tags=["Authentication"],
)
class LoginUserView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    serializer_class = AuthTokenSerializer


@extend_schema(
    summary="Logout User",
    description="Delete the current user's authentication token upon logout.",
    request=None,
    responses={
        200: {
            "description": "Exit successful.",
            "type": "object",
            "properties": {
                "detail": {"type": "string", "description": "Successful exit notification."}
            }
        },
        401: {"description": "The user is not authenticated."},
    },
    tags=["Authentication"],
)
class LogoutUserView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        request.user.auth_token.delete()
        return Response({"detail": "Successfully logged out"}, status=status.HTTP_200_OK)
