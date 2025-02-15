from django.urls import path, include
from rest_framework import routers
from interactions.views import LikeUnlikeDislikeViewSet


app_name = "interactions"

router = routers.DefaultRouter()

router.register("likes", LikeUnlikeDislikeViewSet, basename="like")

urlpatterns = [
    path("", include(router.urls)),
]
