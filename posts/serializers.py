from rest_framework import serializers
from posts.models import Post, Hashtag


class PostSerializers(serializers.ModelSerializer):
    hashtags = serializers.PrimaryKeyRelatedField(queryset=Hashtag.objects.all(), many=True, required=False)
    author_name = serializers.SerializerMethodField(method_name="get_author_username")

    class Meta:
        model = Post
        fields = ("id", "content", "image", "hashtags", "update", "created", "author_name")

    def get_author_username(self, post):
        return post.author.user.username

    def create(self, validate_data):
        validate_data.pop("hashtags", [])
        post = Post.objects.create(**validate_data)
        return post

    def update(self, instance, validated_data):
        validated_data.pop("hashtags", [])
        instance = super().update(instance, validated_data)
        return instance


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ("id", "name", )
