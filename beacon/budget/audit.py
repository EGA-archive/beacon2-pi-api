
from functools import wraps

from beacon.conf.conf_override import config

from beacon.exceptions import (
    NumberOfQueriesExceeded,
    NoPermissionsAvailable
)


def audit_budget(func):

    @wraps(func)
    def wrapper(self, user_id, *args, **kwargs):

        try:

            result = func(self, user_id, *args, **kwargs)

            self.audit.capture_budget_decision(
                decision="allowed",
                previous_query_counts=result["counts"]
            )

            return result["time"]

        except NumberOfQueriesExceeded as exc:

            self.audit.capture_budget_decision(
                decision="rejected",
                previous_query_counts=getattr(
                    exc,
                    "budget_counts",
                    {"user": None, "ip": None}
                ),
                reason="query_limit_exceeded"
            )

            raise

        except NoPermissionsAvailable as exc:

            self.audit.capture_budget_decision(
                decision="rejected",
                previous_query_counts=getattr(
                    exc,
                    "budget_counts",
                    {"user": None, "ip": None}
                ),
                reason="authentication_required"
            )

            raise

    return wrapper
