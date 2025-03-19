from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.models import Profile
from comments.models import Comment
from comments.serializers import CommentSerializers
from interactions.models import Subscription
from posts.models import Post, Hashtag
from posts.serializers import HashtagSerializer, PostListSerializers, PostSerializers, PostRetrieveSerializer
from posts.filters import PostFilter


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostListSerializers
    filterset_class = PostFilter

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializers
        elif self.action == "retrieve":
            return PostRetrieveSerializer
        return PostSerializers

    def get_queryset(self):
        user_profile = Profile.objects.select_related("user").get(user=self.request.user)
        following_profiles = Subscription.objects.filter(follower=self.request.user).values_list("following", flat=True)

        if self.action in ("list", "retrieve"):
            return Post.objects.filter(author__in=[user_profile] + list(following_profiles)). \
                prefetch_related("hashtags")

    def perform_create(self, serializer):
        user_profile = Profile.objects.get(user=self.request.user)
        post = serializer.save(author=user_profile)
        post.extract_hashtags()

    def perform_update(self, serializer):
        post = serializer.save()
        post.extract_hashtags()

    @action(detail=False, methods=["get"])
    def by_hashtag(self, request) -> Response:
        hashtag_name = request.query_params.get("hashtag")
        if not hashtag_name:
            return Response({"error": "Hashtag is required"}, status=status.HTTP_400_BAD_REQUEST)
        hashtag = Hashtag.objects.filter(name=hashtag_name).first()
        if not hashtag:
            return Response({"message": "No posts found for this hashtag"}, status=status.HTTP_404_NOT_FOUND)

        posts = hashtag.posts.all()
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)


class HashtagViewSet(viewsets.ModelViewSet):
    queryset = Hashtag.objects.all()
    serializer_class = HashtagSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializers

    def get_queryset(self):
        post_id = self.kwargs.get("post_pk")
        return Comment.objects.filter(post_id=post_id)

    def perform_create(self, serializer):
        post_id = self.kwargs.get("post_pk")
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return Response({"detail": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer.save(user=self.request.user, post=post)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        instance.delete()
