"""Utilities for mapping Pydantic model fields to ComfyUI node input definitions."""

from enum import Enum
from typing import Any, Type

from comfy.comfy_types.node_typing import IO


def model_field_to_node_input(
    io_type: IO,
    model_cls,
    field_name: str,
    enum_type: Type[Enum] = None,
    **kwargs,
) -> tuple:
    """Convert a Pydantic model field to a ComfyUI node INPUT_TYPES entry.

    Extracts the field description from the Pydantic model to use as a tooltip,
    and builds the appropriate (type, options) tuple for ComfyUI node definitions.

    Args:
        io_type: The ComfyUI IO type (e.g. IO.STRING, IO.FLOAT, IO.COMBO).
        model_cls: The Pydantic model class containing the field.
        field_name: The name of the field on the model.
        enum_type: For IO.COMBO, the Enum class whose values become the options list.
        **kwargs: Additional options to include (e.g. default, min, max, multiline).

    Returns:
        A tuple suitable for use in ComfyUI INPUT_TYPES dicts.
    """
    tooltip = ""
    field = (model_cls.model_fields or {}).get(field_name)
    if field is not None and field.description:
        tooltip = field.description

    options: dict[str, Any] = {}
    if tooltip:
        options["tooltip"] = tooltip
    options.update(kwargs)

    if io_type == IO.COMBO and enum_type is not None:
        values = [e.value for e in enum_type]
        if "default" not in options and values:
            options["default"] = values[0]
        return (values, options)

    return (io_type, options)
