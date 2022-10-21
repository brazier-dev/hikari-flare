import abc
import enum
import inspect
import types
import typing

from flare import exceptions

T = typing.TypeVar("T")


class Converter(abc.ABC, typing.Generic[T]):
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
        # The `IntConverter` will be used to serialize and deserialize this kwarg.
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


_converters: dict[typing.Any, type[Converter[typing.Any]]] = {}


def add_converter(t: typing.Any, converter: type[Converter[typing.Any]]) -> None:
    """
    Set a converter to be used for a certain type hint and the subclasses of the
    type hint.
    """
    _converters[t] = converter


def _any_issubclass(t: typing.Any, cls: typing.Any) -> bool:
    if not inspect.isclass(t):
        return False
    return issubclass(t, cls)


def _is_union(obj: typing.Any) -> bool:
    origin = typing.get_origin(obj)
    return origin is types.UnionType or origin is typing.Union


def _get_left(obj: typing.Any) -> typing.Any:
    if not _is_union(obj):
        return obj
    return typing.get_args(obj)[0]


def get_converter(t: typing.Any) -> Converter[typing.Any]:
    """Internal
    Return the converter used for a certain type hint. If a Union is passed,
    the left side of the Union will be used to find the converter.
    """
    origin = _get_left(t)

    if origin_ := typing.get_origin(origin):
        origin = origin_

    converter = _converters.get(origin)

    if converter:
        return converter(t)

    for k, v in _converters.items():
        if _any_issubclass(t, k):
            return v(t)

    raise exceptions.ConverterError(
        f"Could not find converter for type `{getattr(t, '__name__', t)}`."
    )


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
add_converter(typing.Literal, StringConverter)
add_converter(enum.Enum, EnumConverter)
