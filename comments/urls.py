from django.urls import path, include
from comments.views import CommentViewSet
from rest_framework import routers


app_name = "comments"

router = routers.DefaultRouter()

router.register("comments", CommentViewSet, basename="comment")

urlpatterns = [
    path("", include(router.urls)),
]
