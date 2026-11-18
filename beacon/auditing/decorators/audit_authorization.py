
import inspect
from functools import wraps

from beacon.auditing.context import current_audit, current_handler
from beacon.auditing.actions import SemanticActionResolver
from beacon.auditing.models import Action, Target, Outcome

def audit_authorization(func):
    """
    Decorator that automatically captures dataset authorization
    decisions and records them in the current audit context.

    It wraps an authorization function without modifying its
    original implementation or return value.

    After the original function executes successfully, it:

        - Retrieves the current audit context.
        - Extracts the requested datasets from the function
          arguments, supporting both positional and keyword
          arguments.
        - Identifies which datasets were authorized and rejected.
        - Retrieves the requested granularity from the current
          HTTP handler, when available.
        - Records an authorization decision for each requested
          dataset.
        - Records the corresponding semantic actions.

    For authorized datasets, it captures:
        - Dataset identifier.
        - Security level.
        - Maximum allowed granularity.
        - Requested granularity.
        - Authorization result.
        - Authorization reason.

    For rejected datasets, it records the dataset identifier,
    the failed authorization decision and the reason.

    The effective granularity is initially set to None because
    it can only be established after inspecting the actual API
    response.

    The audit context and handler are retrieved through their
    respective ContextVars, keeping authorization auditing
    independent of the authorization implementation.

    If no audit context exists, the original function executes
    normally without generating audit information.
    """

    # Inspect the original function signature to identify
    # its arguments independently of how they are passed.
    signature = inspect.signature(func)

    @wraps(func)
    async def wrapper(self, *args, **kwargs):

        # Execute the original authorization function.
        result = await func(self, *args, **kwargs)

        # Retrieve the audit context associated with this request.
        audit = current_audit.get()

        if audit is None:
            return result

        # Recover arguments regardless of positional/keyword usage.
        bound = signature.bind_partial(
            self,
            *args,
            **kwargs
        )

        # Extract the datasets requested by the client.
        requested_datasets = (
            bound.arguments.get("requested_datasets") or []
        )

        # Retrieve the datasets returned by the authorization function.
        authorized_datasets = result or []

        # Extract the identifiers of authorized datasets.
        authorized_ids = {
            dataset.dataset
            for dataset in authorized_datasets
        }

        # Convert requested datasets into a set for comparison.
        requested_ids = set(requested_datasets)

        # Retrieve the current HTTP handler to access request information.
        handler = current_handler.get()

        requested_granularity = None

        # Capture the granularity requested by the client, if available.
        if handler:
            requested_granularity = (
                handler.request_attributes
                .qparams.query.requestedGranularity
            )

        decisions = []

        # Create an authorization decision for every authorized dataset.
        for dataset in authorized_datasets:

            decisions.append({
                "dataset": dataset.dataset,
                "security_level": dataset.security_level,
                "allowed": True,
                "requested_granularity": requested_granularity,
                "allowed_granularity": dataset.granularity,
                "effective_granularity": None,
                "reason": "permission_granted"
            })

        # Identify requested datasets that were not authorized.
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

        # Update the authorization section of the audit record
        # with the requested, authorized and rejected datasets.
        audit.update_authorization(
            requested_datasets=sorted(requested_ids),
            authorized_datasets=sorted(authorized_ids),
            rejected_datasets=sorted(requested_ids - authorized_ids),
            decisions=decisions
        )

        # Record the semantic action for successfully authorized datasets.
        if authorized_ids:
            audit.record_semantic_action(
                SemanticActionResolver.resolve_event(
                    "authorization.granted",
                    outcome=Outcome.success
                )
            )

        # Record the semantic action for rejected datasets.
        if requested_ids - authorized_ids:
            audit.record_semantic_action(
                SemanticActionResolver.resolve_event(
                    "authorization.denied",
                    outcome=Outcome.denied
                )
            )

        # Preserve the original authorization function's return value.
        return result

    return wrapper
