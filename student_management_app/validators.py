import warnings
from pathlib import Path

from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError


MAX_PROFILE_PHOTO_SIZE = 5 * 1024 * 1024
MAX_PROFILE_PHOTO_PIXELS = 20_000_000
PROFILE_PHOTO_FORMATS = {
    ".jpg": "JPEG",
    ".jpeg": "JPEG",
    ".png": "PNG",
    ".webp": "WEBP",
}


def validate_profile_photo(uploaded_file):
    extension = Path(uploaded_file.name).suffix.lower()
    expected_format = PROFILE_PHOTO_FORMATS.get(extension)
    if expected_format is None:
        raise ValidationError("Use a JPG, JPEG, PNG, or WebP image.")
    if uploaded_file.size > MAX_PROFILE_PHOTO_SIZE:
        raise ValidationError("Profile photos must be 5 MB or smaller.")

    try:
        uploaded_file.seek(0)
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(uploaded_file) as image:
                if image.format != expected_format:
                    raise ValidationError("The file extension does not match the image content.")
                if image.width * image.height > MAX_PROFILE_PHOTO_PIXELS:
                    raise ValidationError("The image dimensions are too large.")
                image.verify()
    except ValidationError:
        raise
    except (
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
        OSError,
        UnidentifiedImageError,
        ValueError,
    ) as error:
        raise ValidationError("Upload a valid JPG, JPEG, PNG, or WebP image.") from error
    finally:
        uploaded_file.seek(0)
