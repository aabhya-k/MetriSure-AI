from flask import Flask, render_template, request
from datetime import date
import os
from werkzeug.utils import secure_filename

from ocr import run_ocr
from field_extractor import extract_fields

from rules import evaluate_rule, calculate_compliance_score, get_overall_status
from legal.legal_matrix import LEGAL_MATRIX
from legal.versions import get_legal_version
from legal.conditions import build_applicability, get_conditional_requirements


app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ============================================================
# INSPECTION CONTEXT
# ============================================================

INSPECTION_CONTEXT = {
    "commodity_category": "food",
    "is_imported": False,
    "is_ecommerce": False,
    "is_multi_product": False,
    "has_sticker": False,
    "is_retail_package": True,
    "is_time_sensitive": False,
    "is_scheduled_commodity": False,
    "package_shape": "rectangular",
}


# ============================================================
# CONVERT OCR EXTRACTED FIELDS INTO EVIDENCE
# ============================================================

def build_evidence_from_fields(extracted_fields):

    evidence = {}

    # Manufacturer / Packer / Importer
    manufacturer = extracted_fields.get("manufacturer")

    evidence["PCR-01"] = {
        "found": bool(manufacturer),
        "confidence": 0.90 if manufacturer else 0.0,
        "text": manufacturer or ""
    }

    # Country of Origin
    country = extracted_fields.get("country_of_origin")

    evidence["PCR-02"] = {
        "found": bool(country),
        "confidence": 0.90 if country else 0.0,
        "text": country or ""
    }

    # Generic product name
    # We don't currently have a dedicated extractor for this.
    evidence["PCR-03"] = {
        "found": False,
        "confidence": 0.0,
        "text": ""
    }

    # Multiple product declaration
    evidence["PCR-04"] = {
        "found": False,
        "confidence": 0.0,
        "text": ""
    }

    # Net quantity
    quantity = extracted_fields.get("net_quantity")

    evidence["PCR-05"] = {
        "found": bool(quantity),
        "confidence": 0.90 if quantity else 0.0,
        "text": quantity or ""
    }

    # Date information
    evidence["PCR-06"] = {
        "found": False,
        "confidence": 0.0,
        "text": ""
    }

    # Best before / Use by
    evidence["PCR-07"] = {
        "found": False,
        "confidence": 0.0,
        "text": ""
    }

    # MRP
    mrp = extracted_fields.get("mrp")

    evidence["PCR-08"] = {
        "found": bool(mrp),
        "confidence": 0.90 if mrp else 0.0,
        "text": mrp or ""
    }

    # Consumer care
    consumer_care = extracted_fields.get("consumer_care")

    evidence["PCR-09"] = {
        "found": bool(consumer_care),
        "confidence": 0.90 if consumer_care else 0.0,
        "text": consumer_care or ""
    }

    # Standard pack size
    evidence["PCR-10"] = {
        "found": False,
        "confidence": 0.0,
        "text": ""
    }

    # Principal display panel
    evidence["PCR-11"] = {
        "found": True,
        "confidence": 0.80,
        "text": "Package image received for inspection"
    }

    # Declaration visibility
    evidence["PCR-12"] = {
        "found": True,
        "confidence": 0.80,
        "text": "Visual inspection available"
    }

    # Sticker compliance
    evidence["PCR-13"] = {
        "found": False,
        "confidence": 0.0,
        "text": ""
    }

    # E-commerce declarations
    evidence["PCR-14"] = {
        "found": False,
        "confidence": 0.0,
        "text": ""
    }

    # Category-specific exception
    evidence["PCR-15"] = {
        "found": True,
        "confidence": 0.80,
        "text": "Category-specific rule routing available"
    }

    # PDP area
    evidence["PCR-16"] = {
        "found": True,
        "confidence": 0.80,
        "text": "Package display area available for inspection"
    }

    return evidence


# ============================================================
# RUN INSPECTION
# ============================================================

def run_inspection(extracted_fields=None):

    if extracted_fields is None:
        extracted_fields = {}

    inspection_date = date.today()

    legal_version = get_legal_version(
        inspection_date.isoformat()
    )

    applicability = build_applicability(
        INSPECTION_CONTEXT,
        inspection_date.isoformat()
    )

    conditions = get_conditional_requirements(
        INSPECTION_CONTEXT,
        inspection_date.isoformat()
    )

    # Build evidence from the ACTUAL uploaded image fields
    evidence_data = build_evidence_from_fields(
        extracted_fields
    )

    results = []

    for rule_id in LEGAL_MATRIX:

        evidence = evidence_data.get(
            rule_id,
            {
                "found": False,
                "confidence": 0.0,
                "text": ""
            }
        )

        result = evaluate_rule(
            rule_id=rule_id,
            evidence_found=evidence["found"],
            confidence=evidence["confidence"],
            applicable=applicability.get(
                rule_id,
                True
            ),
        )

        result["evidence"] = evidence["text"]

        results.append(result)

    score = calculate_compliance_score(
        results
    )

    overall_status = get_overall_status(
        results
    )

    return {
        "results": results,
        "score": score,
        "status": overall_status,
        "legal_version": legal_version,
        "conditions": conditions,
        "inspection_date": inspection_date.isoformat(),
    }


# ============================================================
# MAIN PAGE
# ============================================================

@app.route("/", methods=["GET", "POST"])
def index():

    inspection = None
    uploaded_filename = None
    ocr_text = ""
    extracted_fields = {}

    if request.method == "POST":

        # Camera upload
        uploaded_file = request.files.get(
            "package_image"
        )

        # Gallery upload fallback
        if (
            not uploaded_file
            or not uploaded_file.filename
        ):
            uploaded_file = request.files.get(
                "package_image_gallery"
            )

        if (
            uploaded_file
            and uploaded_file.filename
        ):

            uploaded_filename = secure_filename(
                uploaded_file.filename
            )

            image_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                uploaded_filename
            )

            uploaded_file.save(
                image_path
            )

            # ----------------------------------------
            # OCR
            # ----------------------------------------

            try:

                ocr_text = run_ocr(
                    image_path
                )

            except Exception as error:

                ocr_text = (
                    f"OCR error: {error}"
                )

            # ----------------------------------------
            # FIELD EXTRACTION
            # ----------------------------------------

            try:

                extracted_fields = extract_fields(
                    ocr_text
                )

            except Exception as error:

                extracted_fields = {
                    "mrp": None,
                    "net_quantity": None,
                    "consumer_care": None,
                    "manufacturer": None,
                    "country_of_origin": None,
                }

                print(
                    "Field extraction error:",
                    error
                )

            # ----------------------------------------
            # RUN REAL INSPECTION
            # USING EXTRACTED FIELDS
            # ----------------------------------------

            inspection = run_inspection(
                extracted_fields
            )

    return render_template(
        "index.html",
        inspection=inspection,
        uploaded_filename=uploaded_filename,
        ocr_text=ocr_text,
        extracted_fields=extracted_fields,
    )


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )