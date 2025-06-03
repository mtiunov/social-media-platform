from django.contrib.auth import get_user_model
from rest_framework import serializers
from accounts.models import Profile
from interactions.models import LikeUnlikeDislike, Subscription
from posts.models import Post

User = get_user_model()


class DetailPostSerializers(serializers.ModelSerializer):
    content = serializers.SerializerMethodField(method_name="get_post_content")

    class Meta:
        model = Post
        fields = ("id", "content")

    def get_post_content(self, likeUnlikeDislike):
        return likeUnlikeDislike.content[:100]


class LikeUnlikeDislikeSerializers(serializers.ModelSerializer):
    post = DetailPostSerializers(read_only=True)
    post_id = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all(), write_only=True, source="post")
    user = serializers.SerializerMethodField(method_name="get_user_username")

    class Meta:
        model = LikeUnlikeDislike
        fields = ("id", "user", "post", "post_id", "value", "created", "update")
        read_only_fields = ("id", "user", "post", "created", "update")

    def get_user_username(self, likeUnlikeDislike):
        return likeUnlikeDislike.user.user.username

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.method != "POST":
            self.fields.pop("post_id", None)


class ProfileSerializers(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Profile
        fields = ("id", "username", "email", "bio", "location")


class SubscriptionSerializers(serializers.ModelSerializer):
    follower_profile = ProfileSerializers(source="follower.profile", read_only=True)
    following = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)
    following_profile = ProfileSerializers(source="following.profile", read_only=True)

    class Meta:
        model = Subscription
        fields = ("id", "follower_profile", "following", "following_profile", "created")
        read_only_fields = ("id", "follower_profile", "following_profile", "created")

    def validate(self, data):
        request = self.context.get("request")

        if not request:
            raise serializers.ValidationError({"Request context is not available."})

        follower = request.user
        following = data.get("following")
        if follower == following:
            raise serializers.ValidationError({"following": ["You cannot subscribe to yourself."]})
        if Subscription.objects.filter(follower=follower, following=following).exists():
            raise serializers.ValidationError({"following": ["You are already following this user."]})
        return data
