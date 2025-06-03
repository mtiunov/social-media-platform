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

    def extract_hashtags(self, post_author):
        if not self.content:
            self.hashtags.set([])
            return
        content_str = str(self.content) if self.content is not None else ""
        hashtags_names = re.findall(r"#(\w+)", content_str)
        tag_objects = []
        for tag_name in hashtags_names:
            hashtag_obj, created = Hashtag.objects.get_or_create(
                name=tag_name.lower(), defaults={"author": post_author}
            )
            tag_objects.append(hashtag_obj)
        self.hashtags.set(tag_objects)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.author:
            self.extract_hashtags(post_author=self.author)


class Hashtag(models.Model):
    name = models.CharField(max_length=255, unique=True)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True, related_name="hashtags")

    def __str__(self) -> str:
        return f"#{self.name}"
