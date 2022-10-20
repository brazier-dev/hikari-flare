import typing

__all__: typing.Sequence[str] = ("FlareException", "ConverterError")


class FlareException(Exception):
    """Base exception class for all flare exceptions."""


class ConverterError(Exception):
    """Exception raised when there is a error with converters."""
