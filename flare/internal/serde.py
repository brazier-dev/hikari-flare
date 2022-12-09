from __future__ import annotations

import abc
import typing as t

from flare.converters import get_converter
from flare.exceptions import SerializerError, SerializerVersionViolation
from flare.utils import gather_iter

if t.TYPE_CHECKING:
    from flare.components import base

__all__: t.Final[t.Sequence[str]] = ("Serde",)


class SerdeABC(abc.ABC):
    """Abstract class for implementing a custom serializer and deserializer."""

    @abc.abstractmethod
    async def serialize(self, cookie: str, types: dict[str, t.Any], kwargs: dict[str, t.Any]) -> str:
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
        self, custom_id: str, map: dict[str, t.Any]
    ) -> tuple[type[base.SupportsCallback[t.Any]], dict[str, t.Any]]:
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

    Args:
        sep:
            The character used to serperate fields.
        null:
            The character used to signify `None`.
        esc:
            The escape character.
        increment_length:
            `increment` is a unique number to allow buttons for the same values in the same
            message. `increment_length` can be set to `0` if identical buttons are never used
            in the same message.
        version:
            The serializer version number.
    """

    def __init__(
        self,
        sep: str = "\x81",
        null: str = "\x82",
        esc: str = "\\",
        increment_length: int = 3,
        version: int | None = 0,
    ) -> None:
        self._SEP: str = sep
        self._ESC: str = esc
        self._NULL: str = null
        self._VER: int | None = version

        self._increment_length = increment_length
        self._increment = 0

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
    def VER(self) -> int | None:
        """
        The version of the serialization format.
        If None, the serializer will not attempt to verify the version of the serialized data.
        """
        return self._VER

    def get_inc(self) -> str:
        self._increment += 1
        if self._increment > 2**self._increment_length - 1:
            self._increment = 0

        return self._increment.to_bytes(self._increment_length, "little").decode("latin1")

    def escape(self, string: str) -> str:
        """Escape a string using `self.ESC`, `self.NULL` and `self.SEP`."""
        out: list[str] = []
        for char in string:
            if char in [self.ESC, self.NULL, self.SEP]:
                out.append(f"{self.ESC}{char}")
            else:
                out.append(char)
        return "".join(out)

    def unescape(self, string: str) -> list[tuple[str, bool]]:
        """Returns a list of tuples signifying (the character, whether it was escaped)"""
        out: list[tuple[str, bool]] = []
        last_was_esc = False

        for char in string:
            if not last_was_esc and char != self.ESC:
                out.append((char, False))
                continue

            if last_was_esc:
                out.append((char, True))
                last_was_esc = False
                continue

            last_was_esc = True

        return out

    async def serialize(self, cookie: str, types: dict[str, t.Any], kwargs: dict[str, t.Any]) -> str:
        version = "" if self.VER is None else await get_converter(int).to_str(self.VER)

        async def serialize_one(k: str, v: t.Any) -> str:
            val = kwargs.get(k)
            converter = get_converter(v)
            return self.escape(await converter.to_str(val)) if val is not None else self.NULL

        out = self.SEP.join(
            (
                f"{version}{self.get_inc()}{self.escape(cookie)}",
                *await gather_iter(serialize_one(k, v) for k, v in types.items()),
            )
        )

        if len(out) > 100:
            raise SerializerError(
                f"The serialized custom_id for component {cookie} may be too long."
                " Try reducing the number of parameters the component takes."
                f" Got length: {len(out)} Expected length: 100 or less"
            )
        return out

    def split_on_sep(self, string: list[tuple[str, bool]]) -> list[list[tuple[str, bool]]]:
        """Split the provided string on the separator, but ignore separators that are escaped.

        Args:
            string:
                The provided string.

        Returns:
            list[str]
                The split string.
        """
        out: list[list[tuple[str, bool]]] = [[]]

        for char, is_escaped in string:
            if char == self.SEP and not is_escaped:
                out.append([])
            else:
                out[-1].append((char, is_escaped))

        return out

    @staticmethod
    def tuple_list_to_string(string: list[tuple[str, bool]]) -> str:
        """Conbine a list of tuples into a string, ignoring the second value."""
        out: list[str] = []
        for char, _ in string:
            out.append(char)
        return "".join(out)

    async def cast_kwargs(self, kwargs: dict[str, t.Any], types: dict[str, t.Any]) -> dict[str, t.Any]:
        ret: dict[str, t.Any] = {}

        async def convert_one(k: str, v: t.Any) -> None:
            if v is None:
                ret[k] = None
                return
            cast_to = types[k]
            ret[k] = await get_converter(cast_to).from_str(v)

        await gather_iter(convert_one(k, v) for k, v in kwargs.items())

        return ret

    async def deserialize(
        self, custom_id: str, map: dict[str, t.Any]
    ) -> tuple[type[base.SupportsCallback[t.Any]], dict[str, t.Any]]:
        if self.VER is not None:  # Allow for no version to disable verification
            version = await get_converter(int).from_str(custom_id[0])

            if version != self.VER:
                raise SerializerVersionViolation(
                    f"Serializer {self.__class__.__name__} cannot deserialize version {version}."
                )

            custom_id = custom_id[1:]

        custom_id = custom_id[self._increment_length :]

        cookie, *args = self.split_on_sep(self.unescape(custom_id))

        component_ = map.get(self.tuple_list_to_string(cookie))

        if component_ is None:
            raise SerializerError(f"Component with cookie {cookie} does not exist.")

        types = component_._dataclass_annotations

        transformed_args: dict[str, t.Any] = {}

        for k, arg in zip(types.keys(), args):
            if len(arg) == 1:
                if arg[0] == (self.NULL, False):
                    transformed_args[k] = None
                    continue
            transformed_args[k] = self.tuple_list_to_string(arg)

        return (component_, await self.cast_kwargs(transformed_args, types))
