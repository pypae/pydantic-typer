from __future__ import annotations

import inspect
import sys
from typing import Any, Callable, TypeVar

KeyType = TypeVar("KeyType")


def deep_update(mapping: dict[KeyType, Any], *updating_mappings: dict[KeyType, Any]) -> dict[KeyType, Any]:
    # Copied from pydantic because they don't expose it publicly:
    # https://github.com/pydantic/pydantic/blob/26129479a06960af9d02d3a948e51985fe59ed4b/pydantic/_internal/_utils.py#L103
    updated_mapping = mapping.copy()
    for updating_mapping in updating_mappings:
        for k, v in updating_mapping.items():
            if k in updated_mapping and isinstance(updated_mapping[k], dict) and isinstance(v, dict):
                updated_mapping[k] = deep_update(updated_mapping[k], v)
            else:
                updated_mapping[k] = v
    return updated_mapping


def inspect_signature(func: Callable[..., Any]) -> inspect.Signature:
    if sys.version_info >= (3, 10):
        signature = inspect.signature(func, eval_str=True)
    else:
        signature = inspect.signature(func)
    return signature
