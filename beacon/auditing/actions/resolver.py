
from beacon.auditing.actions.definitions import (
    SemanticAction,
    RESOURCE_ACTIONS,
)

from beacon.auditing.actions.registry import (
    semantic_action_registry
)

from beacon.auditing.models import (
    Action,
    Category,
    Outcome,
    Target,
)


class SemanticActionResolver:

    def __init__(self, uri_subpath=""):
        self.uri_subpath = uri_subpath.strip("/")

    @staticmethod
    def _get_category(category):

        try:
            return Category(category)
        except (ValueError, TypeError):
            return Category.other

    def resolve(
        self,
        path,
        outcome=Outcome.success,
        target=None,
        reason=None,
        attributes=None
    ):

        path = path.strip("/")

        # Remove the configured Beacon API prefix.
        if self.uri_subpath:

            if path == self.uri_subpath:
                path = ""

            elif path.startswith(self.uri_subpath + "/"):
                path = path[len(self.uri_subpath) + 1:]

        # Extract the endpoint and resource identifier.
        parts = path.split("/") if path else []

        endpoint = parts[0] if parts else ""

        definition = semantic_action_registry.get(endpoint)

        # Resolve unknown dynamically configured endpoints.
        if definition is None:

            name = "beacon.endpoint.query"
            category = Category.other
            target_type = "unknown"
            description = "Query a dynamically configured endpoint"

        else:

            resource_type = definition.resource_type

            category = self._get_category(
                definition.category
            )

            target_type = resource_type
            description = definition.description

            # Resolve resource-specific actions.
            if endpoint in RESOURCE_ACTIONS:

                if len(parts) > 1:
                    name = f"{resource_type}.retrieve"
                    description = (
                        f"Retrieve a specific {resource_type}"
                    )

                else:
                    name = definition.action

            else:

                name = definition.action

        # Construct the action target when one was not supplied.
        if target is None:

            target = Target(
                type=target_type,
                id=parts[1] if len(parts) > 1 else None,
                identifiers=[]
            )

        # Include the semantic description in the action attributes.
        action_attributes = {
            "description": description
        }

        if attributes:
            action_attributes.update(attributes)

        # Return the generated audit Action model.
        return Action(
            name=name,
            category=category,
            target=target,
            outcome=outcome,
            reason=reason,
            attributes=action_attributes
        )

    @staticmethod
    def resolve_event(
        name,
        outcome=Outcome.success,
        target=None,
        reason=None,
        attributes=None
    ):

        definition = semantic_action_registry.get(name)

        # Resolve registered semantic events.
        if definition is not None:

            action_name = definition.action
            category = SemanticActionResolver._get_category(
                definition.category
            )
            description = definition.description
            target_type = definition.resource_type

        else:

            # Support semantic events not explicitly registered.
            action_name = name

            category_name = name.split(".", 1)[0]

            category_mapping = {
                "authentication": Category.authentication,
                "authorization": Category.authorization,
                "database": Category.database,
                "budget": Category.budget,
                "configuration": Category.configuration,
                "administration": Category.administration,
                "health": Category.health,
                "response": Category.system,
                "audit": Category.administration,
                "system": Category.system,
            }

            category = category_mapping.get(
                category_name,
                Category.other
            )

            description = f"Semantic event: {name}"
            target_type = "system"

        # Construct a default target for internal system events.
        if target is None:

            target = Target(
                type=target_type,
                id=None,
                identifiers=[]
            )

        # Include the semantic description in the action attributes.
        action_attributes = {
            "description": description
        }

        if attributes:
            action_attributes.update(attributes)

        return Action(
            name=action_name,
            category=category,
            target=target,
            outcome=outcome,
            reason=reason,
            attributes=action_attributes
        )
