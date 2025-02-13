from rest_framework import serializers
from posts.models import Post


class PostSerializers(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "content", "image", "like", "update", "created", "author")
