from rest_framework import serializers
from comments.models import Comment
from interactions.serializers import DetailPostSerializers
from posts.models import Post


class CommentSerializers(serializers.ModelSerializer):
    post = DetailPostSerializers(read_only=True)
    post_id = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all(), write_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    username = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "user", "username", "post", "post_id", "text", "update", "created")
        read_only_fields = ("id", "post", "created")

    def get_username(self, comment):
        return comment.user.username

    def create(self, validated_data):
        post = validated_data.pop("post_id")
        return Comment.objects.create(post=post, **validated_data)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.method != "POST":
            self.fields.pop("post_id", None)
