from django.contrib.auth import get_user_model
from django.db import models
from accounts.models import Profile
from posts.models import Post

User = get_user_model()


class LikeUnlikeDislike(models.Model):
    class LikeChoices(models.TextChoices):
        LIKE = "like"
        UNLIKE = "Unlike"
        DISLIKE = "Dislike"

    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    value = models.CharField(max_length=8, choices=LikeChoices)
    update = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user}-{self.post}-{self.value}"


class Subscription(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "following")

    def __str__(self) -> str:
        return f"{self.follower} → {self.following}"
