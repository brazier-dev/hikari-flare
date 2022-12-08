import typing

__all__: typing.Sequence[str] = ("FlareException", "ConverterError")


class FlareException(Exception):
    """Base exception class for all flare exceptions."""


class SerializerError(FlareException):
    """An exception raised when a serializer fails to serialize or deserialize."""


class SerializerVersionViolation(SerializerError):
    """An exception raised when a serializer fails to deserialize a custom_id due to a version mismatch."""


class ConverterError(Exception):
    """Exception raised when there is a error with converters."""


class ComponentError(FlareException):
    """Exception raised when there is a error with components."""


class MissingRequiredParameterError(ComponentError):
    """Exception raised when a required parameter (or parameters) for a component is missing."""


class RowMaxWidthError(ComponentError):
    """Exception raised when a row exceeds the maximum width."""


class CustomIDNotSetError(ComponentError):
    """Raised when a component's custom ID is not set because the row it is in was not awaited."""


class ModalError(ComponentError):
    """Raised when there is an error with a modal."""


class TitleNotSetError(ModalError):
    """Raised when a modal is sent before the title is set."""


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
