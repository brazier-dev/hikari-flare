import dataclasses
import typing as t

import sigparse
import typing_extensions

__all__: t.Sequence[str] = ("Dataclass", "Field")


@dataclasses.dataclass
class Field:
    name: str
    default: t.Any
    annotation: t.Any


@typing_extensions.dataclass_transform()
class Dataclass:
    """
    A dataclass impl used for Components.
    This differs from the built-in dataclass because fields optionally can be
    provided as a list of `dataclass.Field` objects instead of as class vars.

    Similar to `dataclasses.dataclass`, `__post_init__` is called after the
    object is constructed.
    """

    _fields: t.ClassVar[list[Field]]
    """The fields that the user adds to the dataclass."""
    _dataclass_annotations: t.ClassVar[dict[str, t.Any]]
    """The types for the dataclass fields that user adds."""

    def __init_subclass__(
        cls,
        fields: list[Field] | None = None,
    ) -> None:
        # class vars are used for fields if fields were provided.
        cls._fields = fields or [
            Field(name=class_var.name, default=class_var.default, annotation=class_var.annotation)
            for class_var in sigparse.classparse(cls)
            if not class_var.name.startswith("_")
        ]

        cls._dataclass_annotations = {field.name: field.annotation for field in cls._fields}

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        """Mapping of field names to field values."""

        left_over = list(self.__class__._fields)[len(args) :]

        for field, value in zip(self.__class__._fields, args):
            setattr(self, field.name, value)

        for field in left_over:
            setattr(self, field.name, kwargs.pop(field.name, field.default))

        self.__post_init__(**kwargs)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({', '.join(f'{k}={repr(v)}' for k,v in self._dataclass_values.items())})"

    def __post_init__(self) -> None:
        """
        Method called after `__init__`. Any kwargs passed into `__init__` that aren't
        part of the dataclass will be passed into __post_int__.
        """
        ...

    @property
    def _dataclass_values(self) -> dict[str, t.Any]:
        return {field.name: getattr(self, field.name) for field in self._fields}


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
