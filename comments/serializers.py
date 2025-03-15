from rest_framework import serializers
from comments.models import Comment


class CommentSerializers(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("id", "user", "post", "text", "update", "created")
