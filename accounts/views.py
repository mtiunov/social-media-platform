from django.http import Http404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.models import Profile
from accounts.serializers import ProfileSerializers


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializers

    def get_queryset(self):
        if self.action == "retrieve":
            return Profile.objects.filter(slug=self.kwargs.get("pk"))
        return Profile.objects.all()

    @action(detail=False, methods=["get"])
    def me(self, request):
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            raise Http404("Profile does not exist.")
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
