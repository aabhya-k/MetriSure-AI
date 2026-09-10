from datetime import date

from rules import (
    evaluate_rule,
    calculate_compliance_score,
    get_overall_status,
)

from legal.legal_matrix import LEGAL_MATRIX
from legal.versions import get_legal_version
from legal.conditions import (
    build_applicability,
    get_conditional_requirements,
)


# ============================================================
# INSPECTION DATE
# ============================================================

INSPECTION_DATE = date.today()


# ============================================================
# SAMPLE PACKAGE CONTEXT
# Change these values for different test cases
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
# SAMPLE OCR / EVIDENCE
# ============================================================

SAMPLE_EVIDENCE = {
    "PCR-01": {
        "found": True,
        "confidence": 0.94,
        "text": "ABC Foods Pvt. Ltd., Bhubaneswar, Odisha",
    },

    "PCR-02": {
        "found": False,
        "confidence": 0.0,
        "text": "",
    },

    "PCR-03": {
        "found": True,
        "confidence": 0.95,
        "text": "Packaged Food Product",
    },

    "PCR-04": {
        "found": False,
        "confidence": 0.0,
        "text": "",
    },

    "PCR-05": {
        "found": True,
        "confidence": 0.96,
        "text": "500 g",
    },

    "PCR-06": {
        "found": False,
        "confidence": 0.0,
        "text": "",
    },

    "PCR-07": {
        "found": False,
        "confidence": 0.0,
        "text": "",
    },

    "PCR-08": {
        "found": True,
        "confidence": 0.98,
        "text": "MRP ₹50",
    },

    "PCR-09": {
        "found": True,
        "confidence": 0.91,
        "text": "Consumer Care: 1800-XXX-XXXX",
    },

    "PCR-10": {
        "found": False,
        "confidence": 0.0,
        "text": "",
    },

    "PCR-11": {
        "found": True,
        "confidence": 0.88,
        "text": "Declaration visible on PDP",
    },

    "PCR-12": {
        "found": True,
        "confidence": 0.93,
        "text": "Declaration clearly visible",
    },

    "PCR-13": {
        "found": False,
        "confidence": 0.0,
        "text": "",
    },

    "PCR-14": {
        "found": False,
        "confidence": 0.0,
        "text": "",
    },

    "PCR-15": {
        "found": True,
        "confidence": 0.90,
        "text": "Standard commodity category",
    },

    "PCR-16": {
        "found": True,
        "confidence": 0.88,
        "text": "PDP dimensions detected",
    },
}


# ============================================================
# HEADER
# ============================================================

def print_header():

    print("\n" + "=" * 65)
    print("       PACKAGED COMMODITY COMPLIANCE ENGINE")
    print("="* 65)


# ============================================================
# LEGAL FRAMEWORK
# ============================================================

def print_legal_framework(legal_version):

    print("\nLEGAL FRAMEWORK")
    print("-" * 65)

    print(
        f"Base Rules       : "
        f"{legal_version['base_version']}"
    )

    print(
        f"Inspection Date  : "
        f"{legal_version['inspection_date']}"
    )

    print(
        f"Active Amendments: "
        f"{legal_version['amendment_count']}"
    )

    if legal_version["active_amendments"]:

        print("\nActive Amendments:")

        for amendment in legal_version["active_amendments"]:

            print(
                f"  • {amendment['amendment_id']} | "
                f"Effective: {amendment['effective_date']}"
            )


# ============================================================
# CONDITIONAL RULES
# ============================================================

def print_conditional_requirements(conditions):

    print("\nCONDITIONAL LEGAL REQUIREMENTS")
    print("-" * 65)

    if not conditions:

        print("No additional conditional requirements triggered.")
        return

    for condition in conditions:

        print(
            f"IF   : {condition['condition']}"
        )

        print(
            f"THEN : {condition['action']}"
        )

        print(
            f"RULE : {condition['rule_id']}"
        )

        print()


# ============================================================
# RESULT DISPLAY
# ============================================================

def print_result(result):

    status = result["status"]

    if status == "PASS":
        icon = "✅"

    elif status == "FAIL":
        icon = "❌"

    elif status == "N/A":
        icon = "➖"

    else:
        icon = "⚠️"

    print(
        f"{icon} {result['name']} | "
        f"Rule: {result['rule_id']} | "
        f"Status: {status} | "
        f"Confidence: {result['confidence']}"
    )

    print(
        f"   Legal Provision: "
        f"{result['provision']}"
    )

    print(
        f"   Reason: "
        f"{result['reason']}"
    )


# ============================================================
# MAIN ENGINE
# ============================================================

def main():

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    print_header()

    # --------------------------------------------------------
    # LEGAL VERSION
    # --------------------------------------------------------

    legal_version = get_legal_version(
        INSPECTION_DATE
    )

    print_legal_framework(
        legal_version
    )

    # --------------------------------------------------------
    # DETERMINE APPLICABILITY
    # --------------------------------------------------------

    applicability = build_applicability(
        INSPECTION_CONTEXT,
        INSPECTION_DATE
    )

    # --------------------------------------------------------
    # GET IF -> THEN CONDITIONS
    # --------------------------------------------------------

    conditional_requirements = (
        get_conditional_requirements(
            INSPECTION_CONTEXT,
            INSPECTION_DATE
        )
    )

    print_conditional_requirements(
        conditional_requirements
    )

    # --------------------------------------------------------
    # COMPLIANCE EVALUATION
    # --------------------------------------------------------

    results = []

    print("\nCOMPLIANCE RESULTS")
    print("-" * 65)

    for rule_id in LEGAL_MATRIX:

        evidence = SAMPLE_EVIDENCE.get(
            rule_id,
            {
                "found": False,
                "confidence": 0.0,
                "text": "",
            },
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

        results.append(result)

        print_result(result)

    # --------------------------------------------------------
    # SCORE
    # --------------------------------------------------------

    score = calculate_compliance_score(
        results
    )

    overall_status = get_overall_status(
        results
    )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    print("\n" + "-" * 65)
    print("COMPLIANCE SUMMARY")
    print("-" * 65)

    print(
        f"Compliance Score : "
        f"{score}%"
    )

    print(
        f"Overall Status   : "
        f"{overall_status}"
    )

    # --------------------------------------------------------
    # EVIDENCE
    # --------------------------------------------------------

    print("\n" + "-" * 65)
    print("EVIDENCE")
    print("-" * 65)

    evidence_count = 0

    for rule_id, evidence in SAMPLE_EVIDENCE.items():

        if evidence["text"]:

            evidence_count += 1

            print(
                f"📌 {rule_id} | "
                f"Text: {evidence['text']} | "
                f"Confidence: {evidence['confidence']}"
            )

    print(
        f"\nEvidence items available: "
        f"{evidence_count}"
    )

    # --------------------------------------------------------
    # COMPLETE
    # --------------------------------------------------------

    print("\n" + "=" * 65)
    print("INSPECTION COMPLETE")
    print("=" * 65)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()