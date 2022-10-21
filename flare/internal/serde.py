from __future__ import annotations

import typing

from flare import converters

if typing.TYPE_CHECKING:
    from flare import component

SEP = "\x01"
ESC = "\\"
ESC_SEP = "\\\x01"
NULL = "\x00"
ESC_NULL = "\\\x00"


def serialize(
    cookie: str, types: dict[str, typing.Any], kwargs: dict[str, typing.Any]
) -> str:
    """
    Encode a custom_id for a component.

    Args:
        cookie:
            A unique identifier for the component.
        types:
            A dictionary of argument names to argument type hints. The type hint
            is used to encode a value to a string.
        kwargs:
            Values that the user passes to save state.
    """
    out = f"{cookie}{SEP}"

    for k, v in types.items():
        val = kwargs.get(k)
        converter = converters.get_converter(v)
        out += f"{(converter.to_str(val) if val else NULL).replace(SEP, ESC_SEP)}{SEP}"

    return out[:-1]


def split_on_sep(s: str) -> list[str]:
    out: list[list[str]] = [[s[0]]]

    for last, char in zip(s[:-1], s[1:]):
        if last != ESC and char == SEP:
            out.append([])
        else:
            out[-1] += [char]

    return ["".join(row).replace(ESC_SEP, SEP) for row in out]


def _cast_kwargs(
    kwargs: dict[str, typing.Any], types: dict[str, typing.Any]
) -> dict[str, typing.Any]:
    ret: dict[str, typing.Any] = {}
    for k, v in kwargs.items():
        cast_to = types[k]
        ret[k] = converters.get_converter(cast_to).from_str(v)

    return ret


def deserialize(
    id: str, map: dict[str, typing.Any]
) -> tuple[component.Component[typing.Any], dict[str, typing.Any]]:
    """
    Decode a custom_id for a component.

    Args:
        id:
            The custom_id of the component.
        map:
            A dictionary of cookies to components.
    """
    cookie, *args = split_on_sep(id)

    component_ = map[cookie]
    types = component_.args

    transformed_args: dict[str, typing.Any] = {}

    for k, arg in zip(types.keys(), args):
        if arg != NULL:
            arg = arg.replace(ESC_NULL, NULL)
            transformed_args[k] = arg

    return (component_, _cast_kwargs(transformed_args, component_.args))
