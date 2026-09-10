import os
from PIL import Image, ImageEnhance, ImageFilter

# PaddleOCR is optional.
# This allows the web app to start on deployments
# where PaddleOCR is not available.
PADDLE_AVAILABLE = False
ocr = None

try:
    # Must be set before importing Paddle/PaddleOCR
    os.environ["FLAGS_use_mkldnn"] = "0"
    os.environ["FLAGS_enable_pir_api"] = "0"

    from paddleocr import PaddleOCR

    ocr = PaddleOCR(
        lang="en",
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
    )

    PADDLE_AVAILABLE = True

except Exception as error:
    print("PaddleOCR unavailable:", error)


def _get_result_data(page):
    """Safely convert a PaddleOCR result into a dictionary."""

    data = page.json

    if callable(data):
        data = data()

    if isinstance(data, dict):
        return data.get("res", data)

    return {}


def run_ocr_detections(image_path):
    """
    Run PaddleOCR and return detected text with
    bounding boxes and confidence scores.
    """

    if not PADDLE_AVAILABLE:
        print("OCR unavailable: PaddleOCR is not installed.")
        return []

    if not os.path.exists(image_path):
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    result = ocr.predict(image_path)

    detections = []

    for page in result:
        data = _get_result_data(page)

        texts = data.get("rec_texts", [])
        scores = data.get("rec_scores", [])
        boxes = data.get("rec_boxes", [])

        for index, text in enumerate(texts):

            if not text or not str(text).strip():
                continue

            score = (
                float(scores[index])
                if index < len(scores)
                else 0.0
            )

            box = (
                boxes[index].tolist()
                if (
                    index < len(boxes)
                    and hasattr(boxes[index], "tolist")
                )
                else (
                    boxes[index]
                    if index < len(boxes)
                    else None
                )
            )

            detections.append({
                "text": str(text).strip(),
                "confidence": round(score, 4),
                "box": box,
            })

    return detections


def _create_mrp_crop(image_path):
    """
    Create a targeted crop around the lower-left package
    declaration area where MRP is printed.
    """

    image = Image.open(image_path).convert("RGB")

    width, height = image.size

    left = 0
    top = 1080
    right = min(width, 450)
    bottom = min(height, 1210)

    crop = image.crop(
        (left, top, right, bottom)
    )

    crop = crop.resize(
        (
            crop.width * 5,
            crop.height * 5,
        ),
        Image.Resampling.LANCZOS,
    )

    crop = ImageEnhance.Contrast(crop).enhance(2.0)
    crop = ImageEnhance.Sharpness(crop).enhance(2.5)

    crop = crop.filter(
        ImageFilter.UnsharpMask(
            radius=1,
            percent=180,
            threshold=2,
        )
    )

    crop_path = os.path.join(
        os.path.dirname(image_path),
        "_mrp_crop.jpeg",
    )

    crop.save(
        crop_path,
        quality=100,
    )

    return crop_path


def run_mrp_ocr(image_path):
    """
    Run targeted OCR on the MRP region.
    """

    if not PADDLE_AVAILABLE:
        return []

    crop_path = _create_mrp_crop(image_path)

    try:
        return run_ocr_detections(crop_path)

    finally:
        if os.path.exists(crop_path):
            os.remove(crop_path)


def run_ocr(image_path):
    """
    Run normal package OCR plus targeted MRP OCR.

    If PaddleOCR is unavailable, return an empty OCR result
    instead of crashing the entire web application.
    """

    if not PADDLE_AVAILABLE:
        print(
            "PaddleOCR is unavailable on this deployment. "
            "Continuing without OCR."
        )
        return ""

    detections = run_ocr_detections(image_path)

    lines = [
        item["text"]
        for item in detections
    ]

    try:
        mrp_detections = run_mrp_ocr(image_path)

        for item in mrp_detections:

            text = item["text"]

            if (
                "rs" in text.lower()
                or "₹" in text
            ):
                lines.append(
                    f"TARGETED_MRP: {text}"
                )

    except Exception as error:
        print(
            "Targeted MRP OCR warning:",
            error,
        )

    return "\n".join(lines)