from django.contrib.auth import get_user_model
from rest_framework import serializers
from accounts.models import Profile
from interactions.models import LikeUnlikeDislike, Subscription

User = get_user_model()


class LikeUnlikeDislikeSerializers(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(method_name="get_user_username")
    post = serializers.SerializerMethodField(method_name="get_post_content")

    class Meta:
        model = LikeUnlikeDislike
        fields = ("id", "user", "post", "value")
        read_only_fields = ("user",)

    def get_user_username(self, likeUnlikeDislike):
        return likeUnlikeDislike.user.user.username

    def get_post_content(self, likeUnlikeDislike):
        return likeUnlikeDislike.post.content[:100]


class ProfileSerializers(serializers.ModelSerializer):
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
        read_only_fields = ("follower", "following_profile")

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
