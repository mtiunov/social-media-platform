from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.models import Profile
from interactions.models import Subscription
from posts.models import Post, Hashtag
from posts.serializers import PostSerializers, HashtagSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializers

    def get_queryset(self):
        user_profile = Profile.objects.get(user=self.request.user)
        following_profile = Subscription.objects.filter(follower=self.request.user).values_list("following", flat=True)
        return Post.objects.filter(author__in=[user_profile] + list(following_profile))

    def perform_create(self, serializer):
        user_profile = Profile.objects.get(user=self.request.user)
        hashtags_data = self.request.data.get("hashtags", [])
        post = serializer.save(author=user_profile)
        hashtags = Hashtag.objects.filter(id__in=hashtags_data)
        post.hashtags.set(hashtags)
        post.extract_hashtags()

    @action(detail=False, methods=["get"])
    def by_hashtag(self, request):
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
