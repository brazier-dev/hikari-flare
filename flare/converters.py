import abc
import enum
import inspect
import typing
from flare import exceptions

T = typing.TypeVar("T")


class Converter(abc.ABC, typing.Generic[T]):
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
    _converters[t] = converter


def _any_issubclass(t: typing.Any, cls: typing.Any) -> bool:
    if not inspect.isclass(t):
        return False
    return issubclass(t, cls)


def get_converter(t: typing.Any) -> Converter[typing.Any]:
    converter = _converters.get(t)

    if converter:
        return converter(t)

    for k, v in _converters.items():
        if _any_issubclass(t, k):
            return v(t)

    raise exceptions.ConverterError(
        f"Could not find converter for type `{t.__name__}`."
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
add_converter(enum.Enum, EnumConverter)
