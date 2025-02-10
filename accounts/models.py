import pathlib
import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify


def profile_image_path(instance: "Profile", filename: str) -> pathlib.Path:
    filename = f"{slugify(instance.get_user_model().username)}-{uuid.uuid4()}" + pathlib.Path(filename).suffix
    return pathlib.Path("upload/avatar/") / pathlib.Path(filename)


class Profile(models.Model):
    class GenderChoices(models.TextChoices):
        FEMALE = "Female"
        MALE = "Male"
        UNKNOWN = "unknown"

    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    bio = models.TextField(default="fill out a bio", max_length=600)
    birthdate = models.DateField(auto_now=False, null=True, blank=True)
    email = models.EmailField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    gender = models.CharField(max_length=50, choices=GenderChoices)
    picture = models.ImageField(upload_to=profile_image_path, blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)
    friends = models.ManyToManyField(get_user_model(), blank=True, related_name="friends")
    update = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user.username} - {self.created}"
