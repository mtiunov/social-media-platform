import pathlib
import uuid

from django.utils.text import slugify


def universal_image_path(instance, filename: str) -> pathlib.Path:
    if hasattr(instance, "user"):
        username = instance.user.username
    elif hasattr(instance, "author"):
        username = instance.author.last_name
    else:
        raise ValueError("Instance must have either 'user' or 'author' attribute.")
    filename = f"{slugify(username)}-{uuid.uuid4()}" + pathlib.Path(filename).suffix
    return pathlib.Path("upload/") / pathlib.Path(filename)
