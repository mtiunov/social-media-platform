from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from interactions.models import LikeUnlikeDislike, Subscription
from interactions.serializers import LikeUnlikeDislikeSerializers, SubscriptionSerializers
from posts.models import Post

User = get_user_model()


class LikeUnlikeDislikeViewSet(viewsets.ModelViewSet):
    serializer_class = LikeUnlikeDislikeSerializers

    def get_queryset(self):
        return LikeUnlikeDislike.objects.filter(user=self.request.user.profile, value="like")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user.profile)

    def create(self, request, *args, **kwargs):
        user_profile = request.user.profile
        post_id = request.data.get("post")
        value = request.data.get("value")

        if not post_id or not value:
            return Response({"error": "Post and value are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        if value not in ["like", "unlike", "dislike"]:
            return Response({"error": "Invalid value"}, status=status.HTTP_400_BAD_REQUEST)

        like_obj, created = LikeUnlikeDislike.objects.update_or_create(
            user=user_profile, post=post, defaults={"value": value}
        )

        message = f"Post {value.lower()}d successfully" if created else f"Post updated to {value.lower()}"
        return Response({"message": message}, status=status.HTTP_200_OK)


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializers

    def get_queryset(self):
        if self.action == "list":
            return Subscription.objects.filter(follower=self.request.user)
        return super().get_queryset()

    def perform_create(self, serializer):

        follower = self.request.user
        following = serializer.validated_data.get("following")

        if follower == following:
            raise ValidationError("You cannot subscribe on yourself.")

        if Subscription.objects.filter(follower=follower, following=following).exists():
            raise ValidationError("You are already subscribed on this user.")

        serializer.save(follower=follower)

    @action(detail=True, methods=["delete"])
    def unsubscribe(self, request, pk=None):

        following = get_object_or_404(User, id=pk)
        subscription = Subscription.objects.filter(follower=request.user, following=following).first()

        if subscription:
            subscription.delete()
            return Response({"message": "Unsubscribing successful."}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message": "You were not subscribed."}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def following_list(self, request):
        subscription = Subscription.objects.filter(follower=request.user)
        serializer = self.get_serializer(subscription, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def followers_list(self, request):
        subscription = Subscription.objects.filter(following=request.user)
        serializer = self.get_serializer(subscription, many=True)
        return Response(serializer.data)
