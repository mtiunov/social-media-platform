from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, exceptions, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from accounts.filters import ProfileFilter
from accounts.models import Profile
from accounts.serializers import ProfileSerializers


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
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user:
            raise exceptions.PermissionDenied("You do not have permission to update this profile.")
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise exceptions.PermissionDenied("You do not have permission to delete this profile.")
        instance.delete()

    @action(detail=False, methods=["get"])
    def me(self, request):
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            raise Http404("Profile does not exist.")
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
