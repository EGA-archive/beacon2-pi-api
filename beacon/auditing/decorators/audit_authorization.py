from functools import wraps
from beacon.auditing.context import current_audit, current_handler
def audit_authorization(func):

    @wraps(func)
    async def wrapper(self, *args, **kwargs):

        result = await func(self, *args, **kwargs)

        audit = current_audit.get()

        if audit is None:
            return result

        requested_datasets = (
            kwargs.get("requested_datasets") or []
        )

        authorized_datasets = result or []

        authorized_ids = {
            dataset.dataset
            for dataset in authorized_datasets
        }

        requested_ids = set(requested_datasets)

        handler = current_handler.get()

        requested_granularity = (
            handler.request_attributes
            .qparams.query.requestedGranularity
        )

        decisions = []

        for dataset in authorized_datasets:

            decisions.append({
                "dataset": dataset.dataset,
                "security_level": dataset.security_level,
                "allowed": True,
                "requested_granularity": requested_granularity,
                "allowed_granularity": dataset.granularity,
                "effective_granularity": dataset.granularity,
                "reason": "permission_granted"
            })

        for dataset in sorted(requested_ids - authorized_ids):

            decisions.append({
                "dataset": dataset,
                "security_level": None,
                "allowed": False,
                "requested_granularity": requested_granularity,
                "allowed_granularity": None,
                "effective_granularity": None,
                "reason": "not_authorized"
            })

        audit.update_authorization(
            requested_datasets=sorted(requested_ids),
            authorized_datasets=sorted(authorized_ids),
            rejected_datasets=sorted(requested_ids - authorized_ids),
            decisions=decisions
        )

        return result

    return wrapper