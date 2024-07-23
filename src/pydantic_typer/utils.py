from __future__ import annotations

import inspect
import sys
from typing import Any, Callable, TypeVar, get_type_hints

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


def _get_type_hints(func: Callable[..., Any]):
    if sys.version_info >= (3, 9):
        hints = get_type_hints(func, include_extras=True)
    else:
        hints = get_type_hints(func)
    return hints


def inspect_signature(func: Callable[..., Any]) -> inspect.Signature:  # pragma: no cover
    if sys.version_info >= (3, 10):
        signature = inspect.signature(func, eval_str=True)
    else:
        raw_signature = inspect.signature(func)
        type_hints = _get_type_hints(func)
        resolved_params = []
        for p in raw_signature.parameters:
            old_param = raw_signature.parameters[p]
            resolved_params.append(
                inspect.Parameter(old_param.name, old_param.kind, default=old_param.default, annotation=type_hints[p])
            )

        signature = raw_signature.replace(parameters=resolved_params)
    return signature


_T = TypeVar("_T")


def copy_type(_: _T) -> Callable[[Any], _T]:
    """Source https://github.com/python/typing/issues/769#issuecomment-903760354"""
    return lambda x: x
