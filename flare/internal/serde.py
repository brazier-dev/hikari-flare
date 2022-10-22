from __future__ import annotations

import typing

from flare.converters import get_converter
from flare.exceptions import FlareException

if typing.TYPE_CHECKING:
    from flare.components import base

__all__: typing.Final[typing.Sequence[str]] = ("Serde",)


class Serde:
    """A class that handles serialization and deserialization of components."""

    @property
    def SEP(self) -> str:
        return "\x01"

    @property
    def ESC(self) -> str:
        return "\\"

    @property
    def NULL(self) -> str:
        return "\x00"

    @property
    def ESC_NULL(self) -> str:
        return f"{self.ESC}\x00"

    @property
    def ESC_SEP(self) -> str:
        return f"{self.ESC}\x01"

    @property
    def VER(self) -> str:
        """The version of the serialization format."""
        return "0"

    def serialize(self, cookie: str, types: dict[str, typing.Any], kwargs: dict[str, typing.Any]) -> str:
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
        out = f"{self.VER}{cookie}{self.SEP}"

        for k, v in types.items():
            val = kwargs.get(k)
            converter = get_converter(v)
            out += f"{(converter.to_str(val).replace(self.NULL, self.ESC_NULL) if val is not None else self.NULL).replace(self.SEP, self.ESC_SEP)}{self.SEP}"

        return out[:-1]

    def split_on_sep(self, s: str) -> list[str]:
        out: list[list[str]] = [[s[0]]]

        for last, char in zip(s[:-1], s[1:]):
            if last != self.ESC and char == self.SEP:
                out.append([])
            else:
                out[-1] += [char]

        return ["".join(row).replace(self.ESC_SEP, self.SEP) for row in out]

    def _cast_kwargs(self, kwargs: dict[str, typing.Any], types: dict[str, typing.Any]) -> dict[str, typing.Any]:
        ret: dict[str, typing.Any] = {}
        for k, v in kwargs.items():
            cast_to = types[k]
            ret[k] = get_converter(cast_to).from_str(v)

        return ret

    def deserialize(
        self, id: str, map: dict[str, typing.Any]
    ) -> tuple[base.Component[typing.Any], dict[str, typing.Any]]:
        """
        Decode a custom_id for a component.

        Args:
            id:
                The custom_id of the component.
            map:
                A dictionary of cookies to components.
        """
        version = id[0]

        if version != self.VER:
            raise FlareException(f"Serializer {self.__class__.__name__} cannot deserialize version {version}.")

        cookie, *args = self.split_on_sep(id)[1:]

        component_ = map[cookie]
        types = component_.args

        transformed_args: dict[str, typing.Any] = {}

        for k, arg in zip(types.keys(), args):
            if arg != self.NULL:
                arg = arg.replace(self.ESC_NULL, self.NULL)
                transformed_args[k] = arg

        return (component_, self._cast_kwargs(transformed_args, component_.args))
