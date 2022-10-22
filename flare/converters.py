import abc
import enum
import inspect
import types
import typing as t

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

    ```python
    import flare
    import hikari

    class IntConverter(flare.Converter[int]):
        def to_str(self, obj: int) -> str:
            return str(obj)

        def from_str(self, obj: str) -> int:
            return int(obj)

    flare.add_converter(int, IntConverter)

    @flare.button(label="Button", style=hikari.ButtonStyle.PRIMARY)
    async def button(
        ctx: flare.Context,
        # `IntConverter` will be used to serialize and deserialize this kwarg.
        number: int,
    ):
        ...
    ```

    Attributes:
        type:
            The type that is currently being serialized/deserialized. This will be
            different than the generic type if a subclass of the generic type is being
            serialized/deserialized.
    """

    def __init__(self, type: T) -> None:
        super().__init__()
        self.type = type

    @abc.abstractmethod
    def to_str(self, obj: T) -> str:
        ...

    @abc.abstractmethod
    def from_str(self, obj: str) -> T:
        ...


_converters: dict[t.Any, type[Converter[t.Any]]] = {}


def add_converter(t: t.Any, converter: type[Converter[t.Any]]) -> None:
    """
    Set a converter to be used for a certain type hint and the subclasses of the
    type hint.
    """
    _converters[t] = converter


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


def get_converter(type_: t.Any) -> Converter[t.Any]:
    """
    Return the converter used for a certain type hint. If a Union is passed,
    the left side of the Union will be used to find the converter.
    """
    origin = _get_left(type_)

    if origin_ := t.get_origin(origin):
        origin = origin_

    converter = _converters.get(origin)

    if converter:
        return converter(type_)

    for k, v in _converters.items():
        if _any_issubclass(type_, k):
            return v(type_)

    raise exceptions.ConverterError(f"Could not find converter for type `{getattr(type_, '__name__', type_)}`.")


class IntConverter(Converter[int]):
    def to_str(self, obj: int) -> str:
        return str(obj)

    def from_str(self, obj: str) -> int:
        return int(obj)


class StringConverter(Converter[str]):
    def to_str(self, obj: str) -> str:
        return obj

    def from_str(self, obj: str) -> str:
        return obj


class EnumConverter(Converter[enum.Enum]):
    def to_str(self, obj: enum.Enum) -> str:
        return str(obj.value)

    def from_str(self, obj: str) -> enum.Enum:
        return self.type(int(obj))  # type: ignore


add_converter(int, IntConverter)
add_converter(str, StringConverter)
add_converter(t.Literal, StringConverter)
add_converter(enum.Enum, EnumConverter)

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
