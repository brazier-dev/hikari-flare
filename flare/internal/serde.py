from __future__ import annotations

import abc
import typing

from flare.converters import get_converter
from flare.exceptions import SerializerError, SerializerVersionViolation

if typing.TYPE_CHECKING:
    from flare.components import base

__all__: typing.Final[typing.Sequence[str]] = ("Serde",)


class SerdeABC(abc.ABC):
    """Abstract class for implementing a custom serializer and deserializer."""

    @abc.abstractmethod
    async def serialize(self, cookie: str, types: dict[str, typing.Any], kwargs: dict[str, typing.Any]) -> str:
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

    @abc.abstractmethod
    async def deserialize(
        self, custom_id: str, map: dict[str, typing.Any]
    ) -> tuple[type[base.CallbackComponent], dict[str, typing.Any]]:
        """
        Decode a custom_id for a component.

        Args:
            custom_id:
                The custom_id of the component.
            map:
                A dictionary of cookies to components.
        """


class Serde(SerdeABC):
    """
    A class that handles serialization and deserialization of component custom_id encoded data.

    For simple behaviour changes it may be sufficient to subclass this class, but if you desire to completely
    overhaul serialization and deserialization, you may wish to only subclass SerdeABC instead.
    """

    def __init__(self, sep: str = "\x81", null: str = "\x82", esc: str = "\\", version: int | None = 0) -> None:
        self._SEP: str = sep
        self._ESC: str = esc
        self._NULL: str = null
        self._VER: int | None = version

        if len(sep) != 1:
            raise ValueError("Separator must be a single character.")

        if len(null) != 1:
            raise ValueError("Null must be a single character.")

        if len(esc) != 1:
            raise ValueError("Escape must be a single character.")

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
    def VER(self) -> int | None:
        """
        The version of the serialization format.
        If None, the serializer will not attempt to verify the version of the serialized data.
        """
        return self._VER

    async def serialize(self, cookie: str, types: dict[str, typing.Any], kwargs: dict[str, typing.Any]) -> str:
        version = "" if self.VER is None else await get_converter(int).to_str(self.VER)
        out = f"{version}{cookie}{self.SEP}"

        for k, v in types.items():
            val = kwargs.get(k)
            converter = get_converter(v)
            val = (await converter.to_str(val)).replace(self.NULL, self.ESC_NULL) if val is not None else self.NULL
            out += f"{val.replace(self.SEP, self.ESC_SEP)}{self.SEP}"

        out = out[:-1]

        if len(out) > 100:
            raise SerializerError(
                f"The serialized custom_id for component {cookie} may be too long. Try reducing the number of parameters the component takes.\nGot length: {len(out)} Expected length: 100 or less"
            )
        return out

    def split_on_sep(self, string: str) -> list[str]:
        """Split the provided string on the separator, but ignore separators that are escaped.

        Args:
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

    async def _cast_kwargs(self, kwargs: dict[str, typing.Any], types: dict[str, typing.Any]) -> dict[str, typing.Any]:
        ret: dict[str, typing.Any] = {}
        for k, v in kwargs.items():
            cast_to = types[k]
            ret[k] = await get_converter(cast_to).from_str(v)

        return ret

    async def deserialize(
        self, custom_id: str, map: dict[str, typing.Any]
    ) -> tuple[type[base.CallbackComponent], dict[str, typing.Any]]:
        if self.VER is not None:  # Allow for no version to disable verification
            version = await get_converter(int).from_str(custom_id[0])

            if version != self.VER:
                raise SerializerVersionViolation(
                    f"Serializer {self.__class__.__name__} cannot deserialize version {version}."
                )

            custom_id = custom_id[1:]

        cookie, *args = self.split_on_sep(custom_id)

        component_ = map.get(cookie)

        if component_ is None:
            raise SerializerError(f"Component with cookie {cookie} does not exist.")

        types = component_._class_vars

        transformed_args: dict[str, typing.Any] = {}

        for k, arg in zip(types.keys(), args):
            if arg != self.NULL:
                arg = arg.replace(self.ESC_NULL, self.NULL)
                transformed_args[k] = arg

        return (component_, await self._cast_kwargs(transformed_args, types))
