from PIL import Image, ImageEnhance, ImageFilter
import os


def create_mrp_crop(
    input_path,
    output_path="mrp_crop.jpeg",
):
    """
    Create a targeted crop around the actual MRP area.
    """

    if not os.path.exists(input_path):
        raise FileNotFoundError(
            f"Image not found: {input_path}"
        )

    image = Image.open(input_path).convert("RGB")

    width, height = image.size

    print("Original image size:", width, "x", height)

    # The actual MRP value is visually below/left of
    # the '22 MAR 15' declaration.
    #
    # We therefore crop a wider region around that area
    # rather than using only the detected 'MRP:' box.

    left = 0
    top = 1080
    right = min(width, 450)
    bottom = min(height, 1210)

    crop = image.crop(
        (left, top, right, bottom)
    )

    # Enlarge substantially for tiny printed text.
    crop = crop.resize(
        (
            crop.width * 5,
            crop.height * 5,
        ),
        Image.Resampling.LANCZOS,
    )

    # Improve contrast.
    crop = ImageEnhance.Contrast(crop).enhance(2.0)

    # Improve sharpness.
    crop = ImageEnhance.Sharpness(crop).enhance(2.5)

    crop = crop.filter(
        ImageFilter.UnsharpMask(
            radius=1,
            percent=180,
            threshold=2,
        )
    )

    crop.save(
        output_path,
        quality=100,
    )

    print("MRP crop created:", output_path)

    return output_path