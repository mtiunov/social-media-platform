from django.db import models
from accounts.models import Profile
from commonutils.util import universal_image_path


class Post(models.Model):
    content = models.TextField()
    image = models.ImageField(upload_to=universal_image_path, blank=True, null=True)
    like = models.ManyToManyField(Profile, blank=True, related_name="likes")
    update = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="posts")

    def __str__(self):
        return str(self.content[:20])

    class Meta:
        ordering = ("-created",)
