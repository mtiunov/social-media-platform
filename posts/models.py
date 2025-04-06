import re

from django.db import models
from accounts.models import Profile
from commonutils.util import universal_image_path


class Post(models.Model):
    content = models.TextField()
    image = models.ImageField(upload_to=universal_image_path, blank=True, null=True)
    update = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    hashtags = models.ManyToManyField("Hashtag", blank=True, related_name="posts")
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="posts")
    publish_at = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=False)

    def __str__(self) -> str:
        return str(self.content[:20])

    class Meta:
        ordering = ("-created",)

    def extract_hashtags(self):
        hashtags = re.findall(r"#(\w+)", str(self.content))
        tag_objects = [Hashtag.objects.get_or_create(name=tag)[0] for tag in hashtags]
        self.hashtags.set(tag_objects)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.extract_hashtags()


class Hashtag(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return f"#{self.name}"
