LEGAL_MATRIX = {

    "PCR-01": {
        "name": "MANUFACTURER_PACKER_IMPORTER",
        "provision": "Rule 6(1)(a)",
        "description": "Name and address of manufacturer, packer and importer where applicable.",
        "applicability": "ALL_APPLICABLE_PACKAGES",
        "required_evidence": ["manufacturer_name", "address"],
        "validation": "ENTITY_AND_ADDRESS_PRESENT",
        "failure_reason": "Required manufacturer/packer/importer details are missing.",
    },

    "PCR-02": {
        "name": "COUNTRY_OF_ORIGIN",
        "provision": "Rule 6(1)(aa)",
        "description": "Country of origin/manufacture/assembly for imported products.",
        "applicability": "IMPORTED_PRODUCTS",
        "required_evidence": ["country_of_origin"],
        "validation": "COUNTRY_PRESENT_IF_IMPORTED",
        "failure_reason": "Country of origin is required for an imported product.",
    },

    "PCR-03": {
        "name": "COMMON_GENERIC_NAME",
        "provision": "Rule 6(1)(b)",
        "description": "Common or generic name of the commodity.",
        "applicability": "ALL_APPLICABLE_PACKAGES",
        "required_evidence": ["product_name"],
        "validation": "PRODUCT_NAME_PRESENT",
        "failure_reason": "Common/generic name of the commodity is missing.",
    },

    "PCR-04": {
        "name": "MULTI_PRODUCT_DECLARATION",
        "provision": "Rule 6(1)(b)",
        "description": "Name and number/quantity of each product where a package contains multiple products.",
        "applicability": "MULTI_PRODUCT_PACKAGES",
        "required_evidence": ["product_components", "component_quantities"],
        "validation": "ALL_COMPONENTS_DECLARED",
        "failure_reason": "Required details for multiple products are incomplete.",
    },

    "PCR-05": {
        "name": "NET_QUANTITY",
        "provision": "Rule 6(1)(c)",
        "description": "Net quantity expressed using the applicable standard unit or number.",
        "applicability": "ALL_APPLICABLE_PACKAGES",
        "required_evidence": ["net_quantity", "unit"],
        "validation": "QUANTITY_AND_UNIT_PRESENT",
        "failure_reason": "Net quantity declaration is missing or incomplete.",
    },

    "PCR-06": {
        "name": "DATE_INFORMATION",
        "provision": "Rule 6(1)(d)",
        "description": "Month and year of manufacture, pre-packing or import where applicable.",
        "applicability": "APPLICABLE_COMMODITIES",
        "required_evidence": ["manufacturing_date"],
        "validation": "DATE_PRESENT_OR_EXCEPTION",
        "failure_reason": "Required manufacturing/packing/import date information is missing.",
    },

    "PCR-07": {
        "name": "BEST_BEFORE_USE_BY",
        "provision": "Rule 6(1)(da)",
        "description": "Best-before/use-by information for commodities that may become unfit for human consumption after a period.",
        "applicability": "PERISHABLE_OR_TIME_SENSITIVE_COMMODITIES",
        "required_evidence": ["best_before_or_use_by"],
        "validation": "DATE_PRESENT_WHEN_APPLICABLE",
        "failure_reason": "Required best-before/use-by information is missing.",
    },

    "PCR-08": {
        "name": "MRP",
        "provision": "Rule 6(1)(e)",
        "description": "Retail sale price with applicable tax-inclusive declaration.",
        "applicability": "RETAIL_PACKAGES",
        "required_evidence": ["mrp"],
        "validation": "MRP_PRESENT_AND_READABLE",
        "failure_reason": "Required retail sale price declaration is missing or unreadable.",
    },

    "PCR-09": {
        "name": "CONSUMER_CARE",
        "provision": "Rule 6(2)",
        "description": "Consumer complaint contact details including name/address and telephone number, with email where available.",
        "applicability": "ALL_APPLICABLE_PACKAGES",
        "required_evidence": ["consumer_care_name", "consumer_care_address", "phone"],
        "validation": "CONSUMER_CONTACT_PRESENT",
        "failure_reason": "Required consumer-care information is incomplete.",
    },

    "PCR-10": {
        "name": "STANDARD_PACK_SIZE",
        "provision": "Rule 5 + applicable Schedule",
        "description": "Package size must comply with prescribed standard pack-size requirements where applicable.",
        "applicability": "SCHEDULED_COMMODITIES",
        "required_evidence": ["net_quantity", "commodity_category"],
        "validation": "STANDARD_SIZE_CHECK",
        "failure_reason": "Declared package size may not comply with the applicable standard.",
    },

    "PCR-11": {
        "name": "PRINCIPAL_DISPLAY_PANEL",
        "provision": "Rules 7 and 8",
        "description": "Mandatory declarations must appear on the Principal Display Panel as required.",
        "applicability": "ALL_APPLICABLE_PACKAGES",
        "required_evidence": ["pdp_region", "declaration_regions"],
        "validation": "DECLARATIONS_ON_PDP",
        "failure_reason": "One or more mandatory declarations may not be correctly positioned on the Principal Display Panel.",
    },

    "PCR-12": {
        "name": "DECLARATION_VISIBILITY",
        "provision": "Rule 9",
        "description": "Mandatory declarations must be legible and prominent.",
        "applicability": "ALL_APPLICABLE_PACKAGES",
        "required_evidence": ["text_region", "ocr_confidence"],
        "validation": "LEGIBLE_AND_PROMINENT",
        "failure_reason": "Mandatory declaration is not sufficiently legible or prominent.",
    },

    "PCR-13": {
        "name": "STICKER_COMPLIANCE",
        "provision": "Rule 6(3) and 6(4)",
        "description": "Detect potentially prohibited alteration of mandatory declarations using stickers.",
        "applicability": "PACKAGES_WITH_STICKERS",
        "required_evidence": ["sticker_region", "underlying_text"],
        "validation": "STICKER_USAGE_CHECK",
        "failure_reason": "Sticker usage may improperly alter a mandatory declaration.",
    },

    "PCR-14": {
        "name": "E_COMMERCE_DECLARATIONS",
        "provision": "Rule 6(10)",
        "description": "Applicable mandatory declarations must be displayed through e-commerce/digital networks.",
        "applicability": "E_COMMERCE_INSPECTION",
        "required_evidence": ["online_declarations"],
        "validation": "ONLINE_DECLARATIONS_PRESENT",
        "failure_reason": "Required package declarations are missing from the online listing.",
    },

    "PCR-15": {
        "name": "CATEGORY_SPECIFIC_EXCEPTION",
        "provision": "Relevant provisos/exemptions",
        "description": "Route commodities governed by other legislation or specific exemptions for specialized handling.",
        "applicability": "CATEGORY_DEPENDENT",
        "required_evidence": ["commodity_category"],
        "validation": "EXCEPTION_ROUTING",
        "failure_reason": "Commodity requires category-specific legal review.",
    },

    "PCR-16": {
        "name": "PDP_AREA",
        "provision": "Rule 7",
        "description": "Determine the applicable Principal Display Panel area according to package geometry.",
        "applicability": "PACKAGES_REQUIRING_PDP_ANALYSIS",
        "required_evidence": ["package_shape", "package_dimensions"],
        "validation": "PDP_GEOMETRY_CHECK",
        "failure_reason": "Principal Display Panel geometry could not be validated.",
    },
}