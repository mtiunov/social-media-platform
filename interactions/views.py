from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from interactions.models import LikeUnlikeDislike, Subscription
from interactions.serializers import LikeUnlikeDislikeSerializers, SubscriptionSerializers

User = get_user_model()


class LikeUnlikeDislikeViewSet(viewsets.ModelViewSet):
    queryset = LikeUnlikeDislike.objects.all()
    serializer_class = LikeUnlikeDislikeSerializers


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializers

    def get_queryset(self):
        if self.action == "list":
            return Subscription.objects.filter(follower=self.request.user)
        return super().get_queryset()

    def perform_create(self, serializer):

        follower = self.request.user
        following = serializer.validate_data.get("following")

        if follower == following:
            raise ValidationError("You cannot subscribe on yourself")

        if Subscription.objects.filter(follower=follower, following=following).exist():
            raise ValidationError("You are already subscribed on this user.")

        serializer.save(follower=follower)

    def unscribe(self, request, *args, **kwargs):

        follower = kwargs.get("pk")
        following = get_object_or_404(User, id=follower)
        subscription = Subscription.objects.filter(follower=request.user, following=following).first()

        if subscription:
            subscription.delete()
            return Response({"Unsubscribing successful."}, status.HTTP_204_NO_CONTENT)
        else:
            return Response({"You were not subscribed."}, status.HTTP_400_BAD_REQUEST)

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
