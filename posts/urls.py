from django.urls import path, include
from posts.views import PostViewSet
from rest_framework import routers

app_name = "posts"

router = routers.DefaultRouter()
router.register("posts", PostViewSet, basename="post")

urlpatterns = [
    path("", include(router.urls)),
]
