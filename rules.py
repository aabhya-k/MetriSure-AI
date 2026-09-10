from legal.legal_matrix import LEGAL_MATRIX


CONFIDENCE_PASS = 0.85
CONFIDENCE_REVIEW = 0.60


def get_rule(rule_id):
    """
    Get a legal rule from the centralized legal matrix.
    """
    return LEGAL_MATRIX.get(rule_id)


def evaluate_rule(
    rule_id,
    evidence_found,
    confidence=0.0,
    applicable=True,
):
    """
    Evaluate a compliance rule using evidence and confidence.
    """

    rule = get_rule(rule_id)

    if rule is None:
        return {
            "rule_id": rule_id,
            "status": "REVIEW",
            "confidence": confidence,
            "reason": "Rule not found in legal matrix.",
        }

    # Rule does not apply to this product/package
    if not applicable:
        return {
            "rule_id": rule_id,
            "name": rule["name"],
            "provision": rule["provision"],
            "status": "N/A",
            "confidence": confidence,
            "reason": "This requirement is not applicable to the inspected commodity.",
        }

    # No evidence
    if not evidence_found:
        return {
            "rule_id": rule_id,
            "name": rule["name"],
            "provision": rule["provision"],
            "status": "FAIL",
            "confidence": 0.0,
            "reason": rule["failure_reason"],
        }

    # Strong evidence
    if confidence >= CONFIDENCE_PASS:
        return {
            "rule_id": rule_id,
            "name": rule["name"],
            "provision": rule["provision"],
            "status": "PASS",
            "confidence": confidence,
            "reason": "Required declaration found with sufficient confidence.",
        }

    # Medium-confidence evidence
    if confidence >= CONFIDENCE_REVIEW:
        return {
            "rule_id": rule_id,
            "name": rule["name"],
            "provision": rule["provision"],
            "status": "REVIEW",
            "confidence": confidence,
            "reason": "Declaration detected, but confidence is insufficient for automatic approval.",
        }

    # Very weak evidence
    return {
        "rule_id": rule_id,
        "name": rule["name"],
        "provision": rule["provision"],
        "status": "FAIL",
        "confidence": confidence,
        "reason": rule["failure_reason"],
    }


def evaluate_all_rules(evidence_data, applicability=None):
    """
    Evaluate all rules in the centralized legal matrix.

    evidence_data example:

    {
        "PCR-01": {"found": True, "confidence": 0.94},
        "PCR-02": {"found": True, "confidence": 0.97},
        ...
    }

    applicability example:

    {
        "PCR-02": True,
        "PCR-07": False
    }
    """

    if applicability is None:
        applicability = {}

    results = []

    for rule_id in LEGAL_MATRIX:

        evidence = evidence_data.get(
            rule_id,
            {
                "found": False,
                "confidence": 0.0,
            },
        )

        applicable = applicability.get(rule_id, True)

        result = evaluate_rule(
            rule_id=rule_id,
            evidence_found=evidence.get("found", False),
            confidence=evidence.get("confidence", 0.0),
            applicable=applicable,
        )

        results.append(result)

    return results


def calculate_compliance_score(results):
    """
    Calculate percentage score using applicable rules only.
    """

    applicable_results = [
        result
        for result in results
        if result["status"] != "N/A"
    ]

    if not applicable_results:
        return 0.0

    passed = sum(
        1 
        for result in applicable_results
        if result["status"] == "PASS"
    )

    return round(
        (passed / len(applicable_results)) * 100,
        2,
    )


def get_overall_status(results):
    """
    Determine overall inspection status.
    """

    statuses = [
        result["status"]
        for result in results
        if result["status"] != "N/A"
    ]

    if not statuses:
        return "REVIEW"

    if "FAIL" in statuses:
        return "NON_COMPLIANT"

    if "REVIEW" in statuses:
        return "REVIEW_REQUIRED"

    return "COMPLIANT"