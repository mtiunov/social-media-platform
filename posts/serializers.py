from rest_framework import serializers
from posts.models import Post, Hashtag


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ("id", "name",)


class PostSerializers(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField(method_name="get_author_username")

    class Meta:
        model = Post
        fields = ("id", "content", "image", "update", "created", "author_name", "hashtags")

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


class PostListSerializers(PostSerializers):
    hashtags = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name"
    )


class PostRetrieveSerializer(PostSerializers):
    hashtags = HashtagSerializer(many=True)
