from django.urls import path, include
from posts.views import PostViewSet, HashtagViewSet
from rest_framework import routers

app_name = "posts"

router = routers.DefaultRouter()
router.register("posts", PostViewSet, basename="post")
router.register("hashtags", HashtagViewSet, basename="hashtag")


urlpatterns = [
    path("", include(router.urls)),
]
