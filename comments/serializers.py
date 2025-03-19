from rest_framework import serializers
from comments.models import Comment


class CommentSerializers(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Comment
        fields = ("id", "user", "username", "post", "text", "update", "created")
        read_only_fields = ("id", "post", "created")

    username = serializers.SerializerMethodField(read_only=True)

    def get_username(self, comment):
        return comment.user.username
