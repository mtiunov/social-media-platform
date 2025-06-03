from django.urls import path, include
from accounts.views import ProfileViewSet
from rest_framework import routers

app_name = "accounts"

router = routers.DefaultRouter()

router.register("profiles", ProfileViewSet, basename="profile")

urlpatterns = [
    path("", include(router.urls)),
]
