from datetime import date


AMENDMENTS = [

    {
        "amendment_id": "PCR-AM-2025-01",
        "notification": "GSR 778(E)",
        "date": date(2025, 10, 23),
        "effective_date": date(2025, 10, 23),
        "status": "ACTIVE",

        "affected_rules": [
            "PCR-11",
            "PCR-12",
            "PCR-15",
        ],

        "description": (
            "Medical-device packages are subject to applicable "
            "declaration and numeral/letter size provisions under "
            "the Medical Devices Rules, 2017."
        ),

        "category": "MEDICAL_DEVICES",

        "source": (
            "Department of Consumer Affairs - "
            "Legal Metrology (Packaged Commodities) "
            "Amendment Rules, 2025"
        ),
    },


    {
        "amendment_id": "PCR-AM-2025-02",
        "notification": "GSR 881(E)",
        "date": date(2025, 12, 2),
        "effective_date": date(2026, 2, 1),
        "status": "ACTIVE",

        "affected_rules": [
            "PCR-15",
        ],

        "description": (
            "Rule 26(a) provision does not apply to pan masala."
        ),

        "category": "PAN_MASALA",

        "source": (
            "Department of Consumer Affairs - "
            "Legal Metrology (Packaged Commodities) "
            "Second (Amendment) Rules, 2025"
        ),
    },


    {
        "amendment_id": "PCR-AM-2026-01",
        "notification": "GSR 128(E)",
        "date": date(2026, 2, 13),
        "effective_date": date(2026, 7, 1),
        "status": "ACTIVE",

        "affected_rules": [
            "PCR-14",
        ],

        "description": (
            "Every e-commerce entity selling imported products "
            "must provide a searchable and sortable filter "
            "specifying country of origin."
        ),

        "category": "E_COMMERCE_IMPORTED_PRODUCTS",

        "source": (
            "Department of Consumer Affairs - "
            "Legal Metrology (Packaged Commodities) "
            "Amendment Rules, 2026"
        ),
    },


    {
        "amendment_id": "PCR-AM-2026-02",
        "notification": "Second Amendment Rules, 2026",
        "date": date(2026, 4, 27),
        "effective_date": date(2027, 7, 1),
        "status": "FUTURE",

        "affected_rules": [
            "PCR-14",
        ],

        "description": (
            "From 1 July 2027, every e-commerce entity offering "
            "an imported product must ensure that its product "
            "listing contains a searchable and sortable filter "
            "specifying country of origin."
        ),

        "category": "E_COMMERCE_IMPORTED_PRODUCTS",

        "source": (
            "Department of Consumer Affairs - "
            "Legal Metrology (Packaged Commodities) "
            "Second Amendment Rules, 2026"
        ),
    },
]


def get_applicable_amendments(inspection_date):

    if isinstance(inspection_date, str):
        inspection_date = date.fromisoformat(inspection_date)

    return [
        amendment
        for amendment in AMENDMENTS
        if amendment["effective_date"] <= inspection_date
    ]


def get_future_amendments(inspection_date=None):

    if inspection_date is None:
        inspection_date = date.today()

    if isinstance(inspection_date, str):
        inspection_date = date.fromisoformat(inspection_date)

    return [
        amendment
        for amendment in AMENDMENTS
        if amendment["effective_date"] > inspection_date
    ]