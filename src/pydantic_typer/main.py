from __future__ import annotations

import inspect
from functools import wraps
from typing import Any, Callable, overload

import pydantic
from typer import Option, Typer
from typer.main import CommandFunctionType, lenient_issubclass
from typer.models import OptionInfo, ParameterInfo
from typer.utils import _split_annotation_from_typer_annotations
from typing_extensions import Annotated

from pydantic_typer.utils import copy_type, deep_update, inspect_signature

PYDANTIC_FIELD_SEPARATOR = "."


def _flatten_pydantic_model(
    model: pydantic.BaseModel, ancestors: list[str], ancestor_typer_param=None
) -> dict[str, inspect.Parameter]:
    pydantic_parameters = {}
    for field_name, field in model.model_fields.items():
        qualifier = [*ancestors, field_name]
        sub_name = f"_pydantic_{'_'.join(qualifier)}"
        if lenient_issubclass(field.annotation, pydantic.BaseModel):
            # TODO: pass ancestor_typer_param
            params = _flatten_pydantic_model(field.annotation, qualifier)  # type: ignore
            pydantic_parameters.update(params)
        else:
            default = (
                field.default if field.default is not pydantic.fields._Unset else ...  # noqa: SLF001
            )
            # Pydantic stores annotations in field.metadata.
            # If the field is already annotated with a typer.Option or typer.Argument, use that.
            existing_typer_params = [meta for meta in field.metadata if isinstance(meta, ParameterInfo)]
            if existing_typer_params:
                typer_param = existing_typer_params[0]
                if isinstance(typer_param, OptionInfo) and not typer_param.param_decls:
                    # If the the option was not named manually, use the default naming scheme
                    typer_param.param_decls = (f"--{PYDANTIC_FIELD_SEPARATOR.join(qualifier)}",)
            elif ancestor_typer_param:
                typer_param = ancestor_typer_param
            else:
                typer_param = Option(f"--{PYDANTIC_FIELD_SEPARATOR.join(qualifier)}")
            pydantic_parameters[sub_name] = inspect.Parameter(
                sub_name,
                inspect.Parameter.KEYWORD_ONLY,
                annotation=Annotated[field.annotation, typer_param, qualifier],
                default=default,
            )
    return pydantic_parameters


def enable_pydantic(callback: CommandFunctionType) -> CommandFunctionType:
    original_signature = inspect_signature(callback)

    pydantic_parameters = {}
    pydantic_roots = {}
    other_parameters = {}
    for name, parameter in original_signature.parameters.items():
        base_annotation, typer_annotations = _split_annotation_from_typer_annotations(parameter.annotation)
        typer_param = typer_annotations[0] if typer_annotations else None
        if lenient_issubclass(base_annotation, pydantic.BaseModel):
            params = _flatten_pydantic_model(parameter.annotation, [name], typer_param)
            pydantic_parameters.update(params)
            pydantic_roots[name] = base_annotation
        else:
            other_parameters[name] = parameter

    extended_signature = inspect.Signature(
        [*other_parameters.values(), *pydantic_parameters.values()],
        return_annotation=original_signature.return_annotation,
    )

    @copy_type(callback)
    @wraps(callback)
    def wrapper(*args, **kwargs):  # type: ignore[no-untyped-def]
        converted_kwargs = kwargs.copy()
        raw_pydantic_objects: dict[str, Any] = {}
        for kwarg_name in kwargs:
            if kwarg_name in pydantic_parameters:
                kwarg_value = kwargs[kwarg_name]
                converted_kwargs.pop(kwarg_name)
                annotation = pydantic_parameters[kwarg_name].annotation
                _, qualifier = annotation.__metadata__
                for part in reversed(qualifier):
                    kwarg_value = {part: kwarg_value}
                raw_pydantic_objects = deep_update(raw_pydantic_objects, kwarg_value)
        for root_name, value in raw_pydantic_objects.items():
            converted_kwargs[root_name] = pydantic_roots[root_name](**value)
        return callback(*args, **converted_kwargs)

    wrapper.__signature__ = extended_signature  # type: ignore
    # Copy annotations to make forward references work in Python <= 3.9
    wrapper.__annotations__ = {k: v.annotation for k, v in extended_signature.parameters.items()}
    return wrapper


class PydanticTyper(Typer):
    @copy_type(Typer.command)
    def command(self, *args, **kwargs):
        original_decorator = super().command(*args, **kwargs)

        def decorator_override(f: CommandFunctionType) -> CommandFunctionType:
            wrapped_f = enable_pydantic(f)
            return original_decorator(wrapped_f)

        return decorator_override
