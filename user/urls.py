from django.urls import path
from user.views import CreateUserView, ManageUserView, LoginUserView, LogoutUserView

app_name = "user"

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="register"),
    path("me/", ManageUserView.as_view(), name="manage"),
    path("login/", LoginUserView.as_view(), name="api-login"),
    path("logout/", LogoutUserView.as_view(), name="api-logout")
]
