import hashlib
import json


def normalize_query(value):

    if isinstance(value, dict):
        return {
            key: normalize_query(item)
            for key, item in sorted(value.items())
        }

    if isinstance(value, list):
        return [
            normalize_query(item)
            for item in value
        ]

    if value is None:
        return "null"

    return type(value).__name__


def query_fingerprint(command):

    normalized = normalize_query(command)

    serialized = json.dumps(
        normalized,
        sort_keys=True,
        separators=(",", ":")
    )

    return "sha256:" + hashlib.sha256(
        serialized.encode("utf-8")
    ).hexdigest()