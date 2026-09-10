
from __future__ import annotations

import json
import re
import unicodedata
from typing import Any, Dict, List, Optional, Tuple

# ==============================================================================
# SECTION 1 — TEXT NORMALIZATION
# (cleans up common OCR noise before we try to classify anything)
# ==============================================================================

_DIGIT_LOOKALIKES = {"O": "0", "o": "0", "I": "1", "l": "1", "S": "5", "B": "8"}
_NUMERIC_TOKEN_RE = re.compile(r"\b[\dOolIS]{2,}\b")
_WORD_WITH_DIGIT_RE = re.compile(r"\b\w*\d\w*\b")


def _fix_numeric_token(token: str) -> str:
    return "".join(_DIGIT_LOOKALIKES.get(ch, ch) for ch in token)


def _fix_word_with_embedded_digit(token: str) -> str:
    # e.g. "PR1CE" -> "PRICE" ; "5OO" is handled by _fix_numeric_token separately
    fixed = re.sub(r"1", "I", token)
    fixed = re.sub(r"0", "O", fixed)
    return fixed


def clean_ocr_text(text: str) -> str:
    """
    Normalize whitespace/unicode and fix common OCR digit-lookalike
    noise, e.g.:
        "MAXIMUM RETAIL PR1CE Rs 120"  -> "MAXIMUM RETAIL PRICE Rs 120"
        "NET WT 5OO g"                 -> "NET WT 500 g"
    """
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("₹", " ₹ ").replace("Rs.", " Rs. ")
    text = re.sub(r"\s+", " ", text).strip()

    def fix_word(match: re.Match) -> str:
        token = match.group(0)
        if re.search(r"\d", token) and re.search(r"[A-Za-z]", token) and len(token) > 3:
            return _fix_word_with_embedded_digit(token)
        return token

    text = _WORD_WITH_DIGIT_RE.sub(fix_word, text)

    def fix_numeric(match: re.Match) -> str:
        token = match.group(0)
        if re.search(r"\d", token):
            return _fix_numeric_token(token)
        return token

    text = _NUMERIC_TOKEN_RE.sub(fix_numeric, text)
    return text


# ==============================================================================
# SECTION 2 — DECLARATION CLASSIFICATION  (Rule 6(1) categories)
# ==============================================================================
# Every "messy" way of writing the same declaration is mapped here to ONE
# canonical Rule-6 category, e.g.:
#     "MRP incl all taxes" / "Maximum Retail Price" / "M.R.P." / "MRP ₹250"
#         -> all normalize to -> "MRP"

RULE6_DECLARATIONS = [
    "MANUFACTURER_PACKER_IMPORTER",   # Rule 6(1)(a)
    "COUNTRY_OF_ORIGIN",              # Rule 6(1)(aa)
    "COMMODITY_NAME",                 # Rule 6(1)(b)
    "NET_QUANTITY",                   # Rule 6(1)(c)
    "MONTH_YEAR_OF_MANUFACTURE",      # Rule 6(1)(d)
    "BEST_BEFORE_OR_USE_BY",          # Rule 6(1)(da)
    "MRP",                            # Rule 6(1)(e)
    "CONSUMER_CARE",                  # Rule 6(2)
]

# Ordered: more specific patterns are checked before generic ones.
_PATTERNS: List[Tuple[str, re.Pattern, float, str]] = [
    (
        "MRP",
        re.compile(r"\b(m\.?\s?r\.?\s?p\.?|maximum\s+retail\s+price)\b", re.I),
        0.95,
        "Rule 6(1)(e)",
    ),
    (
        "NET_QUANTITY",
        re.compile(
            r"\b(net\s?wt\.?|net\s?weight|net\s?qty\.?|net\s?quantity|net\s?vol\.?|net\s?volume)\b",
            re.I,
        ),
        0.93,
        "Rule 6(1)(c)",
    ),
    (
        "BEST_BEFORE_OR_USE_BY",
        re.compile(r"\b(best\s+before|use\s+by|expiry|exp\.?\s*date)\b", re.I),
        0.9,
        "Rule 6(1)(da)",
    ),
    (
        "MONTH_YEAR_OF_MANUFACTURE",
        re.compile(
            r"\b(mfg\.?\s*date|manufactur(?:ing|e)\s+date|date\s+of\s+manufactur(?:e|ing)|"
            r"pkd\.?\s*date|packed\s+on)\b",
            re.I,
        ),
        0.88,
        "Rule 6(1)(d)",
    ),
    (
        "CONSUMER_CARE",
        re.compile(
            r"\b(consumer\s+care|customer\s+care|customer\s+support|toll[\s-]?free|"
            r"for\s+complaints|care@|support@)\b",
            re.I,
        ),
        0.88,
        "Rule 6(2)",
    ),
    (
        "COUNTRY_OF_ORIGIN",
        re.compile(r"\b(made\s+in|country\s+of\s+origin|origin\s*:)\b", re.I),
        0.92,
        "Rule 6(1)(aa)",
    ),
    (
        "MANUFACTURER_PACKER_IMPORTER",
        re.compile(
            r"\b(manufactured\s+by|mfd\.?\s+by|mfg\.?\s+by|manufacturer|"
            r"packed\s+by|packer|imported\s+by|importer|marketed\s+by)\b",
            re.I,
        ),
        0.9,
        "Rule 6(1)(a)",
    ),
]


def classify_declaration(text: str) -> Tuple[Optional[str], float, Optional[str]]:
    """
    Classify one line of (cleaned) OCR text into a Rule-6 declaration
    category.

    Returns (declaration_type, confidence, rule_reference).
    declaration_type is None if the line matches no known Rule-6
    category (COMMODITY_NAME has no fixed keyword — see
    guess_commodity_name() below for that special case).
    """
    for declaration, pattern, confidence, rule_ref in _PATTERNS:
        if pattern.search(text):
            return declaration, confidence, rule_ref
    return None, 0.0, None


# ==============================================================================
# SECTION 3 — VALUE EXTRACTION
# ==============================================================================

_VALUE_PATTERNS: Dict[str, re.Pattern] = {
    "MRP": re.compile(
        r"(?:m\.?\s?r\.?\s?p\.?|maximum\s+retail\s+price)\D{0,15}"
        r"(₹?\s?(?:rs\.?)?\s?[\d,]+(?:\.\d{1,2})?)",
        re.I,
    ),
    "NET_QUANTITY": re.compile(
        r"(?:net\s?wt\.?|net\s?weight|net\s?qty\.?|net\s?quantity|net\s?vol\.?|net\s?volume)\D{0,5}"
        r"([\d.]+\s?(?:g|gm|gms|kg|ml|l|litre|liters?))",
        re.I,
    ),
    "MANUFACTURER_PACKER_IMPORTER": re.compile(
        r"(?:manufactured\s+by|mfd\.?\s+by|mfg\.?\s+by|manufacturer|packed\s+by|packer|"
        r"imported\s+by|importer|marketed\s+by)\s*[:\-]?\s*(.+)",
        re.I,
    ),
    "COUNTRY_OF_ORIGIN": re.compile(
        r"(?:made\s+in|country\s+of\s+origin|origin\s*:)\s*[:\-]?\s*([A-Za-z ]+)", re.I
    ),
    "CONSUMER_CARE": re.compile(
        r"(?:consumer\s+care|customer\s+care|customer\s+support|toll[\s-]?free|for\s+complaints)\s*"
        r"[:\-]?\s*([\d\-+() ]{6,}|\S.+)",
        re.I,
    ),
    "MONTH_YEAR_OF_MANUFACTURE": re.compile(
        r"(?:mfg\.?\s*date|manufactur(?:ing|e)\s+date|date\s+of\s+manufactur(?:e|ing)|pkd\.?\s*date|"
        r"packed\s+on)\s*[:\-]?\s*(\d{1,2}[/\-.]?\d{0,2}[/\-.]?\d{2,4})",
        re.I,
    ),
    "BEST_BEFORE_OR_USE_BY": re.compile(
        r"(?:best\s+before|use\s+by|expiry|exp\.?\s*date)\s*[:\-]?\s*"
        r"(\d{1,2}[/\-.]?\d{0,2}[/\-.]?\d{2,4}|\d+\s*(?:months|days|years))",
        re.I,
    ),
}


def extract_value(declaration: str, cleaned_text: str) -> Optional[str]:
    """Pull just the value portion out of a cleaned OCR line for a given Rule-6 category."""
    pattern = _VALUE_PATTERNS.get(declaration)
    if not pattern:
        return None
    match = pattern.search(cleaned_text)
    if not match:
        return None
    value = match.group(1).strip().rstrip(".,;:-")
    return value or None


# ==============================================================================
# SECTION 4 — CONFIDENCE BANDING
# ==============================================================================

def rule_certainty(ocr_confidence: float, nlp_confidence: float, has_value: bool) -> str:
    """Coarse HIGH / MEDIUM / LOW band a downstream rule engine can use."""
    combined = (ocr_confidence + nlp_confidence) / 2
    if not has_value:
        return "LOW"
    if combined >= 0.85:
        return "HIGH"
    if combined >= 0.6:
        return "MEDIUM"
    return "LOW"


# ==============================================================================
# SECTION 5 — RULE 8 CHECK (Principal Display Panel placement)
# ==============================================================================

def _bbox_inside(inner: List[float], outer: List[float]) -> bool:
    """True if `inner` bbox [x1,y1,x2,y2] lies fully within `outer` bbox."""
    ix1, iy1, ix2, iy2 = inner
    ox1, oy1, ox2, oy2 = outer
    return ix1 >= ox1 and iy1 >= oy1 and ix2 <= ox2 and iy2 <= oy2


def check_rule8_placement(
    declarations: List[Dict[str, Any]], pdp_bbox: Optional[List[float]]
) -> List[Dict[str, Any]]:
    """
    Rule 8(1): every declaration required under Rule 6 must appear on
    the Principal Display Panel (PDP).

    If `pdp_bbox` (the PDP's own [x1,y1,x2,y2] on the image) is
    supplied, this flags every declaration whose bbox falls outside
    it as a Rule 8 placement issue. If `pdp_bbox` is None, this check
    is skipped (returns declarations unchanged) since PDP boundary
    detection is outside this NLP module's scope.
    """
    if pdp_bbox is None:
        return declarations

    for decl in declarations:
        bbox = decl.get("bbox")
        if bbox is None:
            decl["rule8_on_pdp"] = None
        else:
            decl["rule8_on_pdp"] = _bbox_inside(bbox, pdp_bbox)
    return declarations


# ==============================================================================
# SECTION 6 — MAIN PIPELINE: OCR results -> structured Rule-6 declarations
# ==============================================================================

def process_ocr_results(
    ocr_results: List[Dict[str, Any]], pdp_bbox: Optional[List[float]] = None
) -> List[Dict[str, Any]]:
    """
    Run the full NLP pipeline over Member 2's OCR output.

    Args:
        ocr_results: list of {"text": str, "bbox": [x1,y1,x2,y2], "confidence": float}
        pdp_bbox: optional [x1,y1,x2,y2] of the Principal Display Panel,
                  for the Rule 8 placement check (see check_rule8_placement).

    Returns:
        A list of dicts, one per recognized Rule-6 declaration:
        {
            "declaration": "MRP",                 # canonical Rule-6 category
            "rule_reference": "Rule 6(1)(e)",      # exact PDF rule citation
            "value": "250",                        # extracted value (or None)
            "bbox": [40, 60, 420, 100],             # preserved from OCR input
            "ocr_confidence": 0.95,
            "nlp_confidence": 0.95,
            "rule_certainty": "HIGH",
            "raw_text": "MRP Rs. 250/- incl. of all taxes",
            "rule8_on_pdp": True | False | None    # only set if pdp_bbox given
        }

    Lines that match no Rule-6 category are simply skipped here (they
    are not declarations this module is responsible for) — nothing is
    discarded upstream, since the caller still has the raw OCR list.
    """
    declarations: List[Dict[str, Any]] = []

    for box in ocr_results:
        raw_text = box.get("text", "")
        cleaned = clean_ocr_text(raw_text)

        declaration, nlp_confidence, rule_ref = classify_declaration(cleaned)
        if declaration is None:
            continue

        value = extract_value(declaration, cleaned)
        ocr_confidence = float(box.get("confidence", 0.0))

        declarations.append(
            {
                "declaration": declaration,
                "rule_reference": rule_ref,
                "value": value,
                "bbox": box.get("bbox"),
                "ocr_confidence": round(ocr_confidence, 4),
                "nlp_confidence": round(nlp_confidence, 4),
                "rule_certainty": rule_certainty(ocr_confidence, nlp_confidence, value is not None),
                "raw_text": raw_text,
            }
        )

    declarations = check_rule8_placement(declarations, pdp_bbox)
    return declarations


def missing_rule6_declarations(declarations: List[Dict[str, Any]]) -> List[str]:
    """
    Convenience helper: which of the 8 Rule-6(1)/(2) categories were
    NOT found in this package's OCR output at all.

    (Note: COMMODITY_NAME is intentionally excluded here — it has no
    fixed keyword to search for, unlike the other 7 categories, so
    completeness for it should be judged by a human inspector or a
    downstream model, not this keyword-based module.)
    """
    checkable = [d for d in RULE6_DECLARATIONS if d != "COMMODITY_NAME"]
    found = {d["declaration"] for d in declarations}
    return [d for d in checkable if d not in found]


# ==============================================================================
# SECTION 7 — SELF-CONTAINED DEMO (runs with zero setup: `python3 <this file>`)
# ==============================================================================

if __name__ == "__main__":
    # Realistic messy OCR sample data — mirrors what Member 2's OCR
    # engine (PaddleOCR/pytesseract) would hand off, typos included.
    sample_ocr_results = [
        {"text": "M.R.P. Rs. 250/- (incl. of all taxes)", "bbox": [40, 60, 420, 100], "confidence": 0.95},
        {"text": "Net Wt. 5OO g", "bbox": [40, 120, 300, 155], "confidence": 0.88},
        {"text": "Manufactured by: XYZ Foods Pvt Ltd, Pune", "bbox": [40, 180, 460, 215], "confidence": 0.91},
        {"text": "Made in India", "bbox": [40, 240, 220, 270], "confidence": 0.97},
        {"text": "Customer Care: 1800-123-4567", "bbox": [40, 300, 380, 335], "confidence": 0.9},
        {"text": "Mfg Date: 03/2026", "bbox": [40, 360, 260, 390], "confidence": 0.86},
        {"text": "Best Before 9 months from mfg date", "bbox": [40, 420, 380, 450], "confidence": 0.84},
        {"text": "Some decorative logo text", "bbox": [40, 480, 200, 510], "confidence": 0.99},
    ]

    # Optional: the Principal Display Panel's own bbox on the image,
    # for the Rule 8 placement check. Pass None if you don't have this.
    principal_display_panel_bbox = [0, 0, 500, 500]

    print("=" * 78)
    print(" RULE 6 & RULE 8 DECLARATION EXTRACTION — DEMO RUN")
    print("=" * 78)

    declarations = process_ocr_results(sample_ocr_results, pdp_bbox=principal_display_panel_bbox)

    print(f"\nFound {len(declarations)} Rule-6 declaration(s):\n")
    for d in declarations:
        print(f"  [{d['declaration']}]  ({d['rule_reference']})")
        print(f"    value           : {d['value']}")
        print(f"    raw OCR text    : {d['raw_text']}")
        print(f"    bbox            : {d['bbox']}")
        print(f"    ocr_confidence  : {d['ocr_confidence']}")
        print(f"    nlp_confidence  : {d['nlp_confidence']}")
        print(f"    rule_certainty  : {d['rule_certainty']}")
        print(f"    on_PDP (Rule 8) : {d['rule8_on_pdp']}")
        print()

    missing = missing_rule6_declarations(declarations)
    print("-" * 78)
    if missing:
        print(f"Missing Rule-6 declarations (not found anywhere in OCR text): {missing}")
    else:
        print("All checkable Rule-6 declarations were found.")
    print("-" * 78)

    print("\nFull JSON output:\n")
    print(json.dumps(declarations, indent=2, ensure_ascii=False))
