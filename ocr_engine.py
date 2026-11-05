"""OCR extraction is never accepted as verified without user confirmation."""
from io import BytesIO
from PIL import Image, ImageOps, ImageEnhance
import pytesseract


def read_image(image_bytes: bytes) -> tuple[str, Image.Image]:
    image = Image.open(BytesIO(image_bytes)).convert('RGB')
    # Upscale small screenshots to improve OCR; no auto-correct of identifiers.
    enhanced = ImageOps.grayscale(image)
    if enhanced.width < 1400:
        ratio = min(3, 1400 / enhanced.width)
        enhanced = enhanced.resize((round(enhanced.width * ratio), round(enhanced.height * ratio)))
    enhanced = ImageEnhance.Contrast(enhanced).enhance(1.7)
    extracted = pytesseract.image_to_string(enhanced, config='--oem 3 --psm 6', lang='eng')
    return extracted, image
