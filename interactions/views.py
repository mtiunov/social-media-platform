from rest_framework import viewsets
from interactions.models import LikeUnlikeDislike
from interactions.serializers import LikeUnlikeDislikeSerializers


class LikeUnlikeDislikeViewSet(viewsets.ModelViewSet):
    queryset = LikeUnlikeDislike.objects.all()
    serializer_class = LikeUnlikeDislikeSerializers
