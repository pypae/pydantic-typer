from __future__ import annotations

import inspect
from functools import wraps
from typing import Any

import click
import pydantic
from typer import BadParameter, Option, Typer
from typer.main import CommandFunctionType, get_click_param, get_params_from_function, lenient_issubclass
from typer.models import OptionInfo, ParameterInfo, ParamMeta
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


def enable_pydantic_type_validation(callback: CommandFunctionType) -> CommandFunctionType:
    original_signature = inspect_signature(callback)

    # Change the annotation of unsupported types to str to be parsed by pydantic.
    # Adapted from https://github.com/tiangolo/typer/blob/95b767e38a98ee287a7a0e28176284836e1188c2/typer/main.py#L543
    # TODO: it's not ideal to call get_params_from_function and get_click_param here,
    # because it will be called in typer again, but the annotations supported by typer are quite dynamic.
    parameters = get_params_from_function(callback)
    updated_parameters = dict(original_signature.parameters)
    for param_name, param in parameters.items():
        original_parameter = original_signature.parameters[param_name]
        if lenient_issubclass(param.annotation, click.Context):
            continue
        # We don't know wheter to use pydantic or typer to parse a param without checking if typer supports it.
        try:
            get_click_param(param)
        except RuntimeError as e:
            # TODO: don't use raw str, but copy other annotations
            updated_parameter = inspect.Parameter(
                param_name, kind=original_parameter.kind, default=original_parameter.default, annotation=str
            )
            updated_parameters[param_name] = updated_parameter

    new_signature = inspect.Signature(
        parameters=list(updated_parameters.values()), return_annotation=original_signature.return_annotation
    )

    @copy_type(callback)
    @wraps(callback)
    def wrapper(*args, **kwargs):  # type: ignore[no-untyped-def]
        bound_params = original_signature.bind(*args, **kwargs)
        for name, value in bound_params.arguments.items():
            type_adapter = pydantic.TypeAdapter(original_signature.parameters[name].annotation)
            try:
                bound_params.arguments[name] = type_adapter.validate_python(value)
            except pydantic.ValidationError as e:
                raise BadParameter(message=e.errors()[0]["msg"], param_hint=name) from e
        callback(*bound_params.args, **bound_params.kwargs)

    wrapper.__signature__ = new_signature  # type: ignore
    # Copy annotations to make forward references work in Python <= 3.9
    wrapper.__annotations__ = {k: v.annotation for k, v in new_signature.parameters.items()}
    return wrapper


class PydanticTyper(Typer):
    @copy_type(Typer.command)
    def command(self, *args, **kwargs):
        original_decorator = super().command(*args, **kwargs)

        def decorator_override(f: CommandFunctionType) -> CommandFunctionType:
            wrapped_f = enable_pydantic(f)
            wrapped_f = enable_pydantic_type_validation(f)
            return original_decorator(wrapped_f)

        return decorator_override
