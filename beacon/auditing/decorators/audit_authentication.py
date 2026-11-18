
from functools import wraps

from beacon.auditing.context import current_audit
from beacon.auditing.actions import SemanticActionResolver
from beacon.auditing.models import Action, Target, Outcome

def audit_authentication(func):
    """
    Decorator that automatically captures authentication results
    and updates the identity section of the current audit record.

    It also records the corresponding semantic action in the
    current audit context.

    If authentication succeeds, it records:
        - authenticated: True
        - user_id: ID of the authenticated user.
        - authentication_method: Authentication mechanism used.
        - authentication_status: success.

    If authentication raises an exception, it records:
        - authenticated: False
        - user_id: None.
        - authentication_method: Authentication mechanism used.
        - authentication_status: failed.

    The audit context is retrieved through the current_audit
    ContextVar, keeping authentication auditing independent
    of the authentication implementation.
    """

    @wraps(func)
    async def wrapper(self, *args, **kwargs):

        try:
            # Execute the original authentication function.
            result = await func(self, *args, **kwargs)

            # Retrieve the audit context associated with this request.
            audit = current_audit.get()

            if audit is not None:

                # Record the successful authentication result.
                audit.update_identity(
                    authenticated=True,
                    user_id=str(result.user_id),
                    authentication_method="Bearer",
                    authentication_status="success"
                )

                # Record the successful authentication semantic action.
                audit.record_semantic_action(
                    SemanticActionResolver.resolve_event(
                        "authentication.success",
                        outcome=Outcome.success
                    )
                )

            return result

        except Exception:

            # Retrieve the audit context in case authentication fails.
            audit = current_audit.get()

            if audit is not None:

                # Record the failed authentication attempt.
                audit.update_identity(
                    authenticated=False,
                    user_id=None,
                    authentication_method="Bearer",
                    authentication_status="failed"
                )

                # Record the failed authentication semantic action.
                audit.record_semantic_action(
                    SemanticActionResolver.resolve_event(
                        "authentication.failure"
                    )
                )

            # Preserve the original exception and its propagation.
            raise

    return wrapper
