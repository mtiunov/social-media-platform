from rest_framework import serializers
from posts.models import Post


class PostSerializers(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "content", "image", "hashtags", "update", "created", "author")

    def create(self, validate_data):
        post = Post.objects.create(**validate_data)
        post.extract_hashtags()
        return post

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.extract_hashtags()
        return instance
