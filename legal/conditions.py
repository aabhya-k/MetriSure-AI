from datetime import date


def build_applicability(context, inspection_date=None):
    """
    Determines which compliance rules apply based on
    the characteristics of the inspected package.
    """

    if inspection_date is None:
        inspection_date = date.today()

    if isinstance(inspection_date, str):
        inspection_date = date.fromisoformat(inspection_date)

    # Default: assume rules apply unless a condition says otherwise
    applicability = {
        "PCR-01": True,
        "PCR-02": False,
        "PCR-03": True,
        "PCR-04": False,
        "PCR-05": True,
        "PCR-06": True,
        "PCR-07": False,
        "PCR-08": True,
        "PCR-09": True,
        "PCR-10": False,
        "PCR-11": True,
        "PCR-12": True,
        "PCR-13": False,
        "PCR-14": False,
        "PCR-15": False,
        "PCR-16": True,
    }

    # ---------------------------------------------------------
    # PACKAGE CONDITIONS
    # ---------------------------------------------------------

    is_imported = context.get("is_imported", False)
    is_multi_product = context.get("is_multi_product", False)
    is_ecommerce = context.get("is_ecommerce", False)
    has_sticker = context.get("has_sticker", False)
    is_scheduled_commodity = context.get(
        "is_scheduled_commodity", False
    )
    is_time_sensitive = context.get(
        "is_time_sensitive", False
    )

    commodity_category = context.get(
        "commodity_category",
        "general"
    ).lower()

    # ---------------------------------------------------------
    # PCR-02 — COUNTRY OF ORIGIN
    # ---------------------------------------------------------

    if is_imported:
        applicability["PCR-02"] = True

    # ---------------------------------------------------------
    # PCR-04 — MULTIPLE PRODUCTS
    # ---------------------------------------------------------

    if is_multi_product:
        applicability["PCR-04"] = True

    # ---------------------------------------------------------
    # PCR-06 — MANUFACTURING / PACKING DATE
    # ---------------------------------------------------------

    # Certain categories have separate governing provisions.
    # Food products may be governed by FSSAI requirements
    # for date declarations.

    if commodity_category in {
        "food",
        "seed",
        "cosmetic",
    }:
        applicability["PCR-06"] = False

    # ---------------------------------------------------------
    # PCR-07 — BEST BEFORE / USE BY
    # ---------------------------------------------------------

    if is_time_sensitive:
        applicability["PCR-07"] = True

    # ---------------------------------------------------------
    # PCR-10 — STANDARD PACK SIZE
    # ---------------------------------------------------------

    if is_scheduled_commodity:
        applicability["PCR-10"] = True

    # ---------------------------------------------------------
    # PCR-13 — STICKER COMPLIANCE
    # ---------------------------------------------------------

    if has_sticker:
        applicability["PCR-13"] = True

    # ---------------------------------------------------------
    # PCR-14 — E-COMMERCE
    # ---------------------------------------------------------

    if is_ecommerce:
        applicability["PCR-14"] = True

    # ---------------------------------------------------------
    # PCR-15 — CATEGORY-SPECIFIC LEGAL ROUTING
    # ---------------------------------------------------------

    special_categories = {
        "medical_device",
        "pan_masala",
        "food",
        "seed",
        "cosmetic",
    }

    if commodity_category in special_categories:
        applicability["PCR-15"] = True

    return applicability


def get_conditional_requirements(
    context,
    inspection_date=None
):
    """
    Returns human-readable IF -> THEN legal conditions
    triggered by the inspection context.
    """

    if inspection_date is None:
        inspection_date = date.today()

    if isinstance(inspection_date, str):
        inspection_date = date.fromisoformat(inspection_date)

    conditions = []

    # Imported product
    if context.get("is_imported", False):
        conditions.append({
            "condition": "IF product is imported",
            "action": "THEN Country of Origin declaration is required",
            "rule_id": "PCR-02",
        })

    # Multiple products
    if context.get("is_multi_product", False):
        conditions.append({
            "condition": "IF package contains multiple products",
            "action": "THEN each product and its quantity must be declared",
            "rule_id": "PCR-04",
        })

    # Time-sensitive commodity
    if context.get("is_time_sensitive", False):
        conditions.append({
            "condition": "IF commodity is time-sensitive",
            "action": "THEN Best Before / Use By information is required",
            "rule_id": "PCR-07",
        })

    # Scheduled commodity
    if context.get("is_scheduled_commodity", False):
        conditions.append({
            "condition": "IF commodity is covered by prescribed pack-size schedules",
            "action": "THEN standard pack-size compliance must be checked",
            "rule_id": "PCR-10",
        })

    # Sticker
    if context.get("has_sticker", False):
        conditions.append({
            "condition": "IF sticker is detected",
            "action": "THEN sticker usage must be legally validated",
            "rule_id": "PCR-13",
        })

    # E-commerce
    if context.get("is_ecommerce", False):
        conditions.append({
            "condition": "IF package is sold through e-commerce",
            "action": "THEN applicable package declarations must be available online",
            "rule_id": "PCR-14",
        })

    # 2026 imported-product e-commerce requirement
    if (
        context.get("is_ecommerce", False)
        and context.get("is_imported", False)
        and inspection_date >= date(2026, 7, 1)
    ):
        conditions.append({
            "condition": (
                "IF imported product is offered through e-commerce "
                "on or after 1 July 2026"
            ),
            "action": (
                "THEN country of origin must be supported by the "
                "required searchable/sortable online filter"
            ),
            "rule_id": "PCR-14",
        })

    # Medical device
    if context.get("commodity_category", "").lower() == "medical_device":
        conditions.append({
            "condition": "IF commodity is a medical device",
            "action": (
                "THEN applicable declaration and "
                "numeral/letter requirements must be routed "
                "through the Medical Devices Rules"
            ),
            "rule_id": "PCR-15",
        })

    # Pan masala
    if (
        context.get("commodity_category", "").lower()
        == "pan_masala"
        and inspection_date >= date(2026, 2, 1)
    ):
        conditions.append({
            "condition": (
                "IF commodity is pan masala and inspection "
                "date is on or after 1 February 2026"
            ),
            "action": (
                "THEN the applicable Rule 26(a) provision "
                "is subject to the pan-masala exception"
            ),
            "rule_id": "PCR-15",
        })

    return conditions