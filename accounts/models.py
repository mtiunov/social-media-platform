import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.template.defaultfilters import slugify

from commonutils.util import universal_image_path


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
    picture = models.ImageField(upload_to=universal_image_path, blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)
    friends = models.ManyToManyField(get_user_model(), blank=True, related_name="friends")
    update = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.first_name and self.last_name:
            to_slug = slugify(f"{self.first_name} {self.last_name}")
            ex = Profile.objects.filter(slug=to_slug).exists()
            while ex:
                to_slug = slugify(f"{self.first_name} {self.last_name} "
                                  f"{str(uuid.uuid4())[:8].replace('-', '').lower()}")
                ex = Profile.objects.filter(slug=to_slug).exists()
        else:
            to_slug = slugify(str(self.user))
        self.slug = to_slug
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.user} - {self.created}"
