import abc
import typing

T = typing.TypeVar("T")


class Converter(abc.ABC, typing.Generic[T]):
    @staticmethod
    @abc.abstractmethod
    def to_str(obj: T) -> str:
        ...

    @staticmethod
    @abc.abstractmethod
    def from_str(obj: str) -> T:
        ...


converters: dict[typing.Any, type[Converter[typing.Any]]] = {}


def add_converter(t: typing.Any, converter: type[Converter[typing.Any]]) -> None:
    converters[t] = converter


class IntConverter(Converter[int]):
    @staticmethod
    def to_str(obj: int) -> str:
        return str(obj)

    @staticmethod
    def from_str(obj: str) -> int:
        return int(obj)


class StringConverter(Converter[str]):
    @staticmethod
    def to_str(obj: str) -> str:
        return obj

    @staticmethod
    def from_str(obj: str) -> str:
        return obj


add_converter(int, IntConverter)
add_converter(str, StringConverter)
