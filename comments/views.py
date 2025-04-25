from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny

from comments.models import Comment
from comments.serializers import CommentSerializers


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related("user", "post")
    serializer_class = CommentSerializers

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated()]
        return [AllowAny()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
