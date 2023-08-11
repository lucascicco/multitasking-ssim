import inspect
import types
from typing import get_args, get_origin

from .exceptions import ClassDictValidationError


def validate_type_to_value(t: type, v) -> None:
    """Validate a runtime value against a type recursively.

    At this point, we assume that the type is a dataclass
    or a primitive type. But we don't support Literal or
    Generic types.
    """
    if isinstance(v, list):
        o_type = get_origin(t)
        list_inner_type: type | None = None
        if o_type is types.UnionType:  # noqa: E721
            for i_t in get_args(t):
                if get_origin(i_t) is list:
                    list_inner_type = get_args(i_t)[0]
                    break
        else:
            list_inner_type = get_args(t)[0]
        if not list_inner_type:
            raise ClassDictValidationError(
                f"Could not find inner type for list {t}",
            )
        for item in v:
            validate_type_to_value(list_inner_type, item)
    elif isinstance(v, dict):
        o_type = get_origin(t)
        if inspect.isclass(t):
            if hasattr(t, "__dataclass_fields__"):
                fields = t.__dataclass_fields__
            else:
                fields = t.__annotations__
            for field_name, field_type in fields.items():
                expected_type = getattr(field_type, "type", field_type)
                f_value = v.get(field_name)
                try:
                    validate_type_to_value(expected_type, f_value)
                except ClassDictValidationError as e:
                    raise ClassDictValidationError(
                        f"Error validating field {field_name}: {e}",
                    ) from e
        elif o_type is dict:
            t_args = get_args(t)
            for key, value in v.items():
                validate_type_to_value(t_args[0], key)
                validate_type_to_value(t_args[1], value)
        elif o_type is types.UnionType:  # noqa: E721
            t_args = get_args(t)
            c_type = None
            for i_t in t_args:
                if inspect.isclass(i_t):
                    c_type = i_t
                    break
            if not c_type:
                raise ClassDictValidationError(
                    f"Could not find class type in {t}",
                )
            validate_type_to_value(c_type, v)
        else:
            raise ClassDictValidationError(
                f"Excepted a class or a dict for a dict value but got type: {type(t)}",
            )
    else:
        v_type = type(v)
        n_type = (t,)
        if get_origin(t) is types.UnionType:  # noqa: E721
            n_type = get_args(t)
        if v_type not in n_type:
            raise ClassDictValidationError(
                f"Value {v} is not of type {n_type}",
            )
