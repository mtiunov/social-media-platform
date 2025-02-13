from rest_framework import viewsets
from accounts.models import Profile
from accounts.serializers import ProfileSerializers


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializers
