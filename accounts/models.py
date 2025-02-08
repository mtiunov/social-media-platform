from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    class GenderChoices(models.TextChoices):
        FEMALE = "Female"
        MALE = "Male"
        UNKNOWN = "unknown"

    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(default="fill out a bio", max_length=600)
    birthdate = models.DateField(auto_now=False, null=True, blank=True)
    email = models.EmailField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    gender = models.CharField(max_length=50, choices=GenderChoices)
    picture = models.ImageField(default="avatar.png", upload_to="")
    slug = models.SlugField(unique=True, blank=True)
    friends = models.ManyToManyField(User, blank=True, related_name="friends")
    update = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user.username} - {self.created}"
