from rest_framework import viewsets
from posts.models import Post
from posts.serializers import PostSerializers


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializers
