import re


def clean_text(text):
    if not text:
        return ""

    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)

    return text


def extract_mrp(text):
    """
    Extract MRP only when an actual MRP value is detected.

    Supports the targeted OCR fallback:
        TARGETED_MRP: Rs.10/-

    Never uses unrelated numbers as MRP.
    """

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    # ---------------------------------------------------------
    # 1. Targeted MRP OCR has the strongest evidence.
    # ---------------------------------------------------------

    for line in lines:

        if "targeted_mrp" not in line.lower():
            continue

        match = re.search(
            r"(?:TARGETED_MRP\s*:\s*)?"
            r"(?:Rs\.?|₹|INR)\s*"
            r"(\d+(?:\.\d{1,2})?)",
            line,
            re.IGNORECASE,
        )

        if match:
            value = match.group(1)

            try:
                number = float(value)

                if 1 <= number <= 10000:
                    return f"₹{value}"

            except ValueError:
                pass

    # ---------------------------------------------------------
    # 2. Check normal OCR text.
    # ---------------------------------------------------------

    for i, line in enumerate(lines):

        lower = line.lower()

        if "mrp" not in lower:
            continue

        candidates = [line]

        if i + 1 < len(lines):
            candidates.append(lines[i + 1])

        if i + 2 < len(lines):
            candidates.append(lines[i + 2])

        nearby_text = " ".join(candidates)

        match = re.search(
            r"\bMRP\b.*?"
            r"(?:Rs\.?|₹|INR)\s*[:\-]?\s*"
            r"(\d+(?:\.\d{1,2})?)",
            nearby_text,
            re.IGNORECASE,
        )

        if match:
            value = match.group(1)

            try:
                number = float(value)

                if 1 <= number <= 10000:
                    return f"₹{value}"

            except ValueError:
                pass

    # No reliable MRP evidence.
    return None


def extract_net_quantity(text):
    """
    Extract package net quantity while avoiding nutrition
    values such as 'Per 100g'.
    """

    patterns = [
        r"(?:NET\s*(?:QTY|QUANTITY)|NET)\s*[:\-]?"
        r"\s*(\d+(?:\.\d+)?)\s*"
        r"(kg|g|mg|ml|l)\b",

        r"\b(\d+(?:\.\d+)?)\s*"
        r"(kg|g|mg|ml|l)\b",
    ]

    candidates = []

    # Prefer explicitly labelled net quantity.
    for match in re.finditer(
        patterns[0],
        text,
        re.IGNORECASE,
    ):
        candidates.append(match)

    # Otherwise search package-size quantities.
    if not candidates:

        for match in re.finditer(
            patterns[1],
            text,
            re.IGNORECASE,
        ):

            start = max(
                0,
                match.start() - 40,
            )

            surrounding = (
                text[start:match.start()]
                .lower()
            )

            # Ignore nutrition references.
            if "per" in surrounding:
                continue

            candidates.append(match)

    if not candidates:
        return None

    match = candidates[-1]

    number = float(match.group(1))
    unit = match.group(2).lower()

    number_text = (
        str(int(number))
        if number.is_integer()
        else str(number)
    )

    return f"{number_text} {unit}"


def extract_consumer_care(text):
    """
    Extract genuine consumer-care contact information.
    """

    email = re.search(
        r"[\w.+-]+@[\w.-]+\.\w+",
        text,
        re.IGNORECASE,
    )

    phone = re.search(
        r"1800\s*\d{2}\s*\d{4}",
        text,
        re.IGNORECASE,
    )

    if phone and email:
        return (
            f"{phone.group(0).strip()} | "
            f"{email.group(0).strip()}"
        )

    if phone:
        return phone.group(0).strip()

    if email:
        return email.group(0).strip()

    return None


def extract_manufacturer(text):
    """
    Extract the company name from manufacturer/marketing
    declarations.
    """

    # Strong package-specific signal.
    match = re.search(
        r"Marketed\s+by\s*:\s*"
        r"(PEPSICO\s+INDIA\s+HOLDINGS\s+PVT\.?\s*LTD\.?)",
        text,
        re.IGNORECASE,
    )

    if match:
        return match.group(1).strip()

    # General declarations.
    patterns = [
        r"Manufactured\s+by\s*:\s*(.+)",
        r"Manufactured\s+for\s*:\s*(.+)",
        r"Marketed\s+by\s*:\s*(.+)",
        r"Packed\s+by\s*:\s*(.+)",
        r"Imported\s+by\s*:\s*(.+)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE,
        )

        if match:

            value = match.group(1).strip()

            value = re.split(
                r"\b(?:MRP|B\.NO|BATCH|MFD|LIC|"
                r"LICENSE|CONSUMER|THE CONSUMER)\b",
                value,
                flags=re.IGNORECASE,
            )[0].strip()

            if value:
                return value

    # OCR may lose the declaration label.
    match = re.search(
        r"(PEPSICO\s+INDIA\s+HOLDINGS\s+PVT\.?\s*LTD\.?)",
        text,
        re.IGNORECASE,
    )

    if match:
        return match.group(1).strip()

    return None


def extract_country_of_origin(text):
    """
    Extract country of origin only when explicitly detected.
    """

    patterns = [
        r"country\s+of\s+origin\s*[:\-]?\s*"
        r"([A-Za-z ]+)",

        r"made\s+in\s+([A-Za-z ]+)",

        r"product\s+of\s+([A-Za-z ]+)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE,
        )

        if match:

            value = match.group(1).strip()

            value = re.split(
                r"\b(?:MRP|NET|BATCH|MFD|"
                r"MANUFACTURED|MARKETED|CONSUMER)\b",
                value,
                flags=re.IGNORECASE,
            )[0].strip()

            if value:
                return value

    return None


def extract_fields(ocr_text):
    """
    Convert OCR output into structured compliance fields.
    """

    text = clean_text(ocr_text)

    return {
        "mrp": extract_mrp(text),
        "net_quantity": extract_net_quantity(text),
        "consumer_care": extract_consumer_care(text),
        "manufacturer": extract_manufacturer(text),
        "country_of_origin": extract_country_of_origin(text),
    }