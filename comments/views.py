from rest_framework import viewsets
from comments.models import Comment
from comments.serializers import CommentSerializers


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializers
