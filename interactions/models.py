from django.db import models
from accounts.models import Profile
from posts.models import Post


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
