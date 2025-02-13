import pathlib
import uuid

from django.utils.text import slugify


def universal_image_path(instance, filename: str) -> pathlib.Path:
    filename = f"{slugify(instance.user.last_name)}-{uuid.uuid4()}" + pathlib.Path(filename).suffix
    return pathlib.Path("upload/") / pathlib.Path(filename)
