
from functools import wraps

from beacon.conf.conf_override import config

from beacon.exceptions.exceptions import (
    NumberOfQueriesExceeded,
    NoPermissionsAvailable
)


def audit_budget(func):

    @wraps(func)
    def wrapper(self, user_id, *args, **kwargs):

        enabled = (
            config.query_budget_per_user
            or config.query_budget_per_ip
        )

        try:
            result = func(self, user_id, *args, **kwargs)

            self.audit.capture_budget_decision(
                enabled=enabled,
                scope=(
                    "user"
                    if user_id is not None
                    and config.query_budget_per_user
                    else "ip"
                    if config.query_budget_per_ip
                    else None
                ),
                period_seconds=config.query_budget_time_in_seconds,
                maximum_queries=config.query_budget_amount,
                previous_query_counts=result.get("counts"),
                decision="allowed",
                reason=None
            )

            return result["time"]

        except NumberOfQueriesExceeded as exc:

            self.audit.capture_budget_decision(
                enabled=enabled,
                scope=(
                    "user"
                    if user_id is not None
                    and config.query_budget_per_user
                    else "ip"
                ),
                period_seconds=config.query_budget_time_in_seconds,
                maximum_queries=config.query_budget_amount,
                previous_query_counts=getattr(
                    exc,
                    "budget_counts",
                    {"user": None, "ip": None}
                ),
                decision="rejected",
                reason="query_limit_exceeded"
            )

            raise

        except NoPermissionsAvailable:

            self.audit.capture_budget_decision(
                enabled=enabled,
                scope="user",
                period_seconds=config.query_budget_time_in_seconds,
                maximum_queries=config.query_budget_amount,
                previous_query_counts={"user": None, "ip": None},
                decision="rejected",
                reason="authentication_required"
            )

            raise

    return wrapper
