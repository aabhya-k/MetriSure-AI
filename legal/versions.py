from datetime import date
from .amendments import get_applicable_amendments


CURRENT_BASE_VERSION = "PCR-2011"


def get_legal_version(inspection_date=None):
    """
    Determine the applicable legal version for an inspection date.
    """

    if inspection_date is None:
        inspection_date = date.today()

    if isinstance(inspection_date, str):
        inspection_date = date.fromisoformat(inspection_date)

    amendments = get_applicable_amendments(inspection_date)

    return {
        "base_version": CURRENT_BASE_VERSION,
        "inspection_date": inspection_date.isoformat(),
        "active_amendments": amendments,
        "amendment_count": len(amendments),
    }


def get_active_amendment_ids(inspection_date=None):
    """
    Return IDs of amendments active on the inspection date.
    """

    version = get_legal_version(inspection_date)

    return [
        amendment["amendment_id"]
        for amendment in version["active_amendments"]
    ]