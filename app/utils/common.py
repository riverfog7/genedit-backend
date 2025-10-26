import io

from PIL import Image


def load_image(image_bytes: bytes):
    return Image.open(io.BytesIO(image_bytes)).convert("RGB")
