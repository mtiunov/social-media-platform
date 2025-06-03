from django.urls import path, include
from rest_framework import routers
from interactions.views import LikeUnlikeDislikeViewSet, SubscriptionViewSet

app_name = "interactions"

router = routers.DefaultRouter()

router.register("likes", LikeUnlikeDislikeViewSet, basename="like")
router.register("subscriptions", SubscriptionViewSet, basename="subscription")

urlpatterns = [
    path("", include(router.urls)),
]
