import dataclasses
import typing as t

import sigparse
import typing_extensions as te

__all__: t.Sequence[str] = ("Dataclass", "Field")


@dataclasses.dataclass
class Field:
    name: str
    default: t.Any
    annotation: t.Any


@te.dataclass_transform()
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
            Field(name=class_var.name, default=class_var.name, annotation=class_var.annotation)
            for class_var in sigparse.classparse(cls)
            if not class_var.name.startswith("_")
        ]

        cls._dataclass_annotations = {field.name: field.annotation for field in cls._fields}

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        left_over = list(self.__class__._fields)[len(args) :]

        for field, value in zip(self.__class__._fields, args):
            setattr(self, field.name, value)

        for field in left_over:
            setattr(self, field.name, kwargs.get(field.name, field.default))

        self.__post_init__()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({', '.join(f'{k}={repr(v)}' for k,v in self._dataclass_values.items())})"

    def __post_init__(self) -> None:
        ...

    @property
    def _dataclass_values(self) -> dict[str, t.Any]:
        return {field.name: getattr(self, field.name) for field in self._fields}
