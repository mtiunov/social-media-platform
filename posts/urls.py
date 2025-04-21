from django.urls import path, include
from rest_framework_nested import routers as nested_routers
from posts.views import PostViewSet, HashtagViewSet
from rest_framework import routers

app_name = "posts"

router = routers.DefaultRouter()
router.register("posts", PostViewSet, basename="post")
router.register("hashtags", HashtagViewSet, basename="hashtag")
router.register("schedules", PostViewSet, basename="schedule")

posts_router = nested_routers.NestedSimpleRouter(router, "posts", lookup="post")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(posts_router.urls)),
]
