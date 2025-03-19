from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404

from comments.models import Comment
from comments.serializers import CommentSerializers
from rest_framework.response import Response


class CommentViewSet(viewsets.ViewSet):

    def list(self, request):
        queryset = Comment.objects.filter(user=request.user)
        serializer = CommentSerializers(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Comment.objects.filter(user=request.user)
        comment = get_object_or_404(queryset, pk=pk)
        serializer = CommentSerializers(comment)
        return Response(serializer.data)

    def update(self, request, pk=None):
        queryset = get_object_or_404(Comment.objects.filter(user=request.user), pk=pk)
        serializer = CommentSerializers(queryset, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        queryset = get_object_or_404(Comment.objects.filter(user=request.user), pk=pk)
        comment = get_object_or_404(queryset, pk=pk)
        return comment.delete()
