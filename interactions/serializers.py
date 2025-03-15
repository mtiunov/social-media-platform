from rest_framework import serializers
from interactions.models import LikeUnlikeDislike, Subscription


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


class SubscriptionSerializers(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ("id", "follower", "following", "created")
        read_only_fields = ("follower", "following")

    def validate(self, data):
        follower = self.context["request"].user
        following = self.data.get("following")

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

        subscription = Subscription.objects.created(follower=following, following=following)
        return subscription
