from django.contrib.auth import get_user_model
from django.db import models
from rest_framework.exceptions import ValidationError
from accounts.models import Profile
from posts.models import Post

User = get_user_model()


class LikeUnlikeDislike(models.Model):
    class LikeChoices(models.TextChoices):
        LIKE = "like", "Like"
        UNLIKE = "Unlike", "Unlike"
        DISLIKE = "dislike", "Dislike"

    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="user_likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_likes")
    value = models.CharField(max_length=8, choices=LikeChoices)
    update = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "post"], name="unique_user_post_like")
        ]

    def __str__(self) -> str:
        return f"{self.user}-{self.post}-{self.value}"

    def clean(self):
        if self.value not in [choice[0] for  choice in self.LikeChoices.choices]:
            raise ValidationError("Invalid value for like/unlike/dislike")


class Subscription(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "following")

    def __str__(self) -> str:
        return f"{self.follower} → {self.following}"
