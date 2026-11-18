
from beacon.auditing.actions.definitions import (
    SemanticAction,
    RESOURCE_ACTIONS,
    FRAMEWORK_ACTIONS,
    SYSTEM_ACTIONS,
)


class SemanticActionRegistry:

    def __init__(self):

        self._actions = {}

        self._actions.update(RESOURCE_ACTIONS)
        self._actions.update(FRAMEWORK_ACTIONS)
        self._actions.update(SYSTEM_ACTIONS)

    def get(self, name):

        return self._actions.get(name)

    def register(self, name, action):

        if not isinstance(action, SemanticAction):
            raise TypeError(
                "Registered actions must be SemanticAction instances"
            )

        if name in self._actions:
            raise ValueError(
                f"Semantic action already registered: {name}"
            )

        if not isinstance(name, str) or not name:
            raise ValueError(
                "Semantic action registry name must be a non-empty string"
            )

        self._actions[name] = action

    def contains(self, name):

        return name in self._actions

    def all(self):

        return dict(self._actions)


semantic_action_registry = SemanticActionRegistry()
