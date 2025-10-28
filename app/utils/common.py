import io

from PIL import Image


def load_image(image_bytes: bytes):
    return Image.open(io.BytesIO(image_bytes)).convert("RGB")


def image_to_bytes(image: Image.Image) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
