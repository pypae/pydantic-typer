from __future__ import annotations

import importlib
import inspect
import re
from functools import wraps
from typing import Any, Callable

import click
import pydantic
from typer import BadParameter, Option
from typer import Typer as TyperBase
from typer.main import CommandFunctionType, get_click_param, get_params_from_function, lenient_issubclass
from typer.models import OptionInfo, ParameterInfo
from typer.utils import (
    AnnotatedParamWithDefaultValueError,
    DefaultFactoryAndDefaultValueError,
    MixedAnnotatedAndDefaultStyleError,
    MultipleTyperAnnotationsError,
    _split_annotation_from_typer_annotations,
)
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
                typer_param: OptionInfo = Option(f"--{PYDANTIC_FIELD_SEPARATOR.join(qualifier)}")

            # Copy Field metadata to Option, fixes https://github.com/pypae/pydantic-typer/issues/2
            if field.description and not typer_param.help:
                typer_param.help = field.description

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


def _recursive_replace_annotation(original_annotation, type_to_replace, replacement):
    if original_annotation == type_to_replace:
        return replacement
    if hasattr(original_annotation, "__origin__"):
        if original_annotation.__origin__ == type_to_replace:
            # This is a pydantic type with extra information, such as:
            # typing.Annotated[pydantic_core._pydantic_core.Url, UrlConstraints(max_length=2083, allowed_schemes=['http', 'https'], host_required=None, default_host=None, default_port=None, default_path=None)]
            return replacement
        if hasattr(original_annotation, "__args__") and hasattr(original_annotation.__origin__, "__getitem__"):
            # This is probably a list or tuple. Replace the error type inside the list/tuple.
            args = tuple(
                _recursive_replace_annotation(arg, type_to_replace, replacement) for arg in original_annotation.__args__
            )
            return original_annotation.__origin__[args]
    return original_annotation


def _parse_error_type(error_message: str) -> type | None:
    match = re.search(r"<class '(.+?)'>", error_message)
    if not match:
        return None

    type_string = match.group(1)
    module_path, class_name = type_string.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def enable_pydantic_type_validation(callback: CommandFunctionType) -> CommandFunctionType:
    original_signature = inspect_signature(callback)
    # Change the annotation of unsupported types to str to be parsed by pydantic.
    # Adapted from https://github.com/tiangolo/typer/blob/95b767e38a98ee287a7a0e28176284836e1188c2/typer/main.py#L543
    # TODO: it's not ideal to call get_params_from_function and get_click_param here,
    # because it will be called in typer again, but the annotations supported by typer are quite dynamic.
    try:
        parameters = get_params_from_function(callback)
    except (
        AnnotatedParamWithDefaultValueError,
        DefaultFactoryAndDefaultValueError,
        MixedAnnotatedAndDefaultStyleError,
        MultipleTyperAnnotationsError,
    ):
        # We can't raise now. Typer will raise in the right moment.
        parameters = {}

    updated_parameters = dict(original_signature.parameters)
    for param_name, param in parameters.items():
        original_parameter = original_signature.parameters[param_name]
        if lenient_issubclass(param.annotation, click.Context):
            # click.Context should not be modified
            continue
        # We don't know wheter to use pydantic or typer to parse a param without checking if typer supports it.
        try:
            get_click_param(param)
        except click.ClickException:
            # We can't raise now. Typer will raise in the right moment.
            continue
        except RuntimeError as e:
            # FIXME: For now, we parse the unsupported type from the RuntimeError.
            error_type = _parse_error_type(str(e))
            updated_annotation = _recursive_replace_annotation(
                original_parameter.annotation,
                error_type,
                str,
            )

            updated_parameter = inspect.Parameter(
                param_name,
                kind=original_parameter.kind,
                default=original_parameter.default,
                annotation=updated_annotation,
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
            try:
                type_adapter = pydantic.TypeAdapter(original_signature.parameters[name].annotation)
            except pydantic.PydanticSchemaGenerationError:
                continue
            try:
                bound_params.arguments[name] = type_adapter.validate_python(value)
            except pydantic.ValidationError as e:
                raise BadParameter(message=e.errors()[0]["msg"], param_hint=name) from e
        callback(*bound_params.args, **bound_params.kwargs)

    wrapper.__signature__ = new_signature  # type: ignore
    # Copy annotations to make forward references work in Python <= 3.9
    wrapper.__annotations__ = {k: v.annotation for k, v in new_signature.parameters.items()}
    return wrapper


class Typer(TyperBase):
    @copy_type(TyperBase.command)
    def command(self, *args, **kwargs):
        original_decorator = super().command(*args, **kwargs)

        def decorator_override(f: CommandFunctionType) -> CommandFunctionType:
            f = enable_pydantic(f)
            f = enable_pydantic_type_validation(f)
            return original_decorator(f)

        return decorator_override


def run(function: Callable[..., Any]) -> None:
    app = Typer(add_completion=False)
    app.command()(function)
    app()
