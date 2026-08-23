from enum import Enum
import datetime

class PolicyVersion(Enum):
    PRE_AMENDMENT = 1
    POST_AMENDMENT = 2
    UNKNOWN = 3

def determine_policy_version(date_str):
    if not date_str:
        return PolicyVersion.UNKNOWN
    try:
        dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        effective_date = datetime.datetime(2026, 3, 1)
        if dt < effective_date:
            return PolicyVersion.PRE_AMENDMENT
        else:
            return PolicyVersion.POST_AMENDMENT
    except ValueError:
        return PolicyVersion.UNKNOWN
