from rest_framework import serializers
from interactions.models import LikeUnlikeDislike


class LikeUnlikeDislikeSerializers(serializers.ModelSerializer):
    class Meta:
        model = LikeUnlikeDislike
        fields = ("id", "user", "post", "value", "update", "created")
