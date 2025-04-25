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
    post_id = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all(), write_only=True)
    user = serializers.SerializerMethodField(method_name="get_user_username")

    class Meta:
        model = LikeUnlikeDislike
        fields = ("id", "user", "post", "post_id", "value", "created", "update")
        read_only_fields = ("user", "post", "created", "update")

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
        read_only_fields = ("id", "follower", "follower_profile", "following_profile", "created")

    def validate(self, data):
        follower = self.context["request"].user
        following = data.get("following")

        if not following:
            raise serializers.ValidationError({"following": "This field is required."})

        if follower == following:
            raise serializers.ValidationError("You cannot subscribe to yourself")

        return data

    def create(self, validated_data):
        follower = self.context["request"].user
        following = validated_data["following"]

        if Subscription.objects.filter(follower=follower, following=following).exists():
            raise serializers.ValidationError("You are already following this user")

        subscription = Subscription.objects.create(follower=follower, following=following)
        return subscription


class SubscriptionUpdateSerializers(serializers.ModelSerializer):
    follower_profile = ProfileSerializers(source="follower.profile", read_only=True)
    following_profile = ProfileSerializers(source="following.profile", read_only=True)
    created = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Subscription
        fields = ("id", "follower_profile", "following_profile", "created")
        read_only_fields = ("id", "follower_profile", "following_profile", "created")
