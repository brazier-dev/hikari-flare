from __future__ import annotations

import typing

from flare.converters import get_converter
from flare.exceptions import FlareException

if typing.TYPE_CHECKING:
    from flare.components import base

__all__: typing.Final[typing.Sequence[str]] = ("Serde",)


class Serde:
    """A class that handles serialization and deserialization of component custom_id encoded data."""

    def __init__(self, sep: str = "\x01", null: str = "\x00", esc: str = "\\", version: str | None = "0") -> None:
        self._SEP: str = sep
        self._ESC: str = esc
        self._NULL: str = null
        self._VER: str | None = version

    @property
    def SEP(self) -> str:
        """The separator used to separate arguments."""
        return self._SEP

    @property
    def ESC(self) -> str:
        """The escape character."""
        return self._ESC

    @property
    def NULL(self) -> str:
        """Character used to represent a missing value."""
        return self._NULL

    @property
    def ESC_NULL(self) -> str:
        """The escape sequence for the null character."""
        return f"{self.ESC}{self.NULL}"

    @property
    def ESC_SEP(self) -> str:
        """The escape sequence for the separator."""
        return f"{self.ESC}{self.SEP}"

    @property
    def VER(self) -> str | None:
        """
        The version of the serialization format.
        If None, the serializer will not attempt to verify the version of the serialized data.
        """
        return self._VER

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

    def split_on_sep(self, string: str) -> list[str]:
        """Split the provided string on the separator, but ignore separators that are escaped.

        Parameters:
            string:
                The provided string.

        Returns:
            list[str]
                The split string.
        """
        out: list[list[str]] = [[string[0]]]

        for last, char in zip(string[:-1], string[1:]):
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
        self, custom_id: str, map: dict[str, typing.Any]
    ) -> tuple[base.Component[typing.Any], dict[str, typing.Any]]:
        """
        Decode a custom_id for a component.

        Args:
            custom_id:
                The custom_id of the component.
            map:
                A dictionary of cookies to components.
        """
        if self.VER:  # Allow for no version to disable verification
            version = custom_id[0]

            if version != self.VER:
                raise FlareException(f"Serializer {self.__class__.__name__} cannot deserialize version {version}.")

            custom_id = custom_id[1:]

        cookie, *args = self.split_on_sep(custom_id)

        component_ = map[cookie]
        types = component_.args

        transformed_args: dict[str, typing.Any] = {}

        for k, arg in zip(types.keys(), args):
            if arg != self.NULL:
                arg = arg.replace(self.ESC_NULL, self.NULL)
                transformed_args[k] = arg

        return (component_, self._cast_kwargs(transformed_args, component_.args))
