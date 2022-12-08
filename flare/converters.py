import abc
import enum
import functools
import inspect
import struct
import types
import typing as t

import hikari.traits

from flare import exceptions

T = t.TypeVar("T")

__all__: t.Final[t.Sequence[str]] = (
    "Converter",
    "add_converter",
    "StringConverter",
    "IntConverter",
    "EnumConverter",
)


class Converter(abc.ABC, t.Generic[T]):
    """
    Converters are used to convert types between a python object and string.

    .. code-block:: python

        import flare
        import hikari

        class IntConverter(flare.Converter[int]):
            async def to_str(self, obj: int) -> str:
                return str(obj)

            async def from_str(self, obj: str) -> int:
                return int(obj)

        flare.add_converter(int, IntConverter)

        @flare.button(label="Button", style=hikari.ButtonStyle.PRIMARY)
        async def button(
            ctx: flare.MessageContext,
            # `IntConverter` will be used to serialize and deserialize this kwarg.
            number: int,
        ):
            ...


    Attributes:
        type:
            The type that is currently being serialized/deserialized. This will be
            different than the generic type if a subclass of the generic type is being
            serialized/deserialized.
    """

    app: t.ClassVar[hikari.traits.EventManagerAware]

    def __init__(self, type: T) -> None:
        super().__init__()
        self.type = type

    @abc.abstractmethod
    async def to_str(self, obj: T) -> str:
        ...

    @abc.abstractmethod
    async def from_str(self, obj: str) -> T:
        ...


_converters: dict[t.Any, tuple[type[Converter[t.Any]], bool]] = {}


def add_converter(t: t.Any, converter: type[Converter[t.Any]], *, supports_subclass: bool = False) -> None:
    """
    Set a converter to be used for a certain type hint and the subclasses of the
    type hint.

    Args:
        t:
            The type this converter supports.
        converter: The converter object.
        supports_subclass:
            If `True`, this converter will be used for subclasses of `t`.
    """
    _converters[t] = (converter, supports_subclass)
    get_converter.cache_clear()


def _any_issubclass(t: t.Any, cls: t.Any) -> bool:
    if not inspect.isclass(t):
        return False
    return issubclass(t, cls)


def _is_union(obj: t.Any) -> bool:
    origin = t.get_origin(obj)
    return origin is types.UnionType or origin is t.Union


def _get_left(obj: t.Any) -> t.Any:
    if not _is_union(obj):
        return obj
    return t.get_args(obj)[0]


@functools.lru_cache(maxsize=128)
def get_converter(type_: t.Any) -> Converter[t.Any]:
    """
    Return the converter used for a certain type hint. If a Union is passed,
    the left side of the Union will be used to find the converter.
    """
    origin = _get_left(type_)

    if origin_ := t.get_origin(origin):
        origin = origin_

    if origin in _converters:
        converter, _ = _converters[origin]
        return converter(origin)
    else:
        for k, (converter, supports_subclass) in _converters.items():
            if supports_subclass and _any_issubclass(origin, k):
                return converter(origin)

    raise exceptions.ConverterError(f"Could not find converter for type `{getattr(type_, '__name__', type_)}`.")


class IntConverter(Converter[int]):
    async def to_str(self, obj: int) -> str:
        byte_length = obj.bit_length() // 8 + 1
        return obj.to_bytes(byte_length, "little").decode("latin1")

    async def from_str(self, obj: str) -> int:
        return self.type.from_bytes(obj.encode("latin1"), "little")


class FloatConverter(Converter[float]):
    async def to_str(self, obj: float) -> str:
        return struct.pack("d", obj).decode("latin1")

    async def from_str(self, obj: str) -> float:
        return struct.unpack("d", obj.encode("latin1"))[0]


class StringConverter(Converter[str]):
    async def to_str(self, obj: str) -> str:
        return obj

    async def from_str(self, obj: str) -> str:
        return obj


class EnumConverter(Converter[enum.Enum]):
    async def to_str(self, obj: enum.Enum) -> str:
        return await get_converter(int).to_str(obj.value)

    async def from_str(self, obj: str) -> enum.Enum:
        return self.type(get_converter(int).from_str(obj))  # type: ignore


class BoolConverter(Converter[bool]):
    async def to_str(self, obj: bool) -> str:
        return "1" if obj else "0"

    async def from_str(self, obj: str) -> bool:
        return bool(int(obj))


add_converter(float, FloatConverter, supports_subclass=True)
add_converter(int, IntConverter, supports_subclass=True)
add_converter(str, StringConverter, supports_subclass=True)
add_converter(t.Literal, StringConverter)
add_converter(enum.Enum, EnumConverter, supports_subclass=True)
add_converter(bool, BoolConverter)

# MIT License
#
# Copyright (c) 2022-present Lunarmagpie
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
