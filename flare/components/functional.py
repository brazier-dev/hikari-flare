from __future__ import annotations

import abc
import typing as t
import typing_extensions as te
import hikari
import sigparse
from flare import dataclass

from flare.components import base
from flare.components.button import Button
from flare.components.select import Select

if t.TYPE_CHECKING:
    from flare import context

__all__: t.Sequence[str] = ("button", "select")

P = te.ParamSpec("P")
T = t.TypeVar("T", bound="base.Component")


class FunctionalComponent(abc.ABC, t.Generic[T]):
    """
    Decorator to wrap a component function callback so it can be treated as a
    class internally. This should be inherited to create decorators for
    specific component types.
    """

    # This function is a python moment.
    # Just trust that it works.
    def __call__(self, callback_: t.Callable[te.Concatenate[context.Context, P], t.Any]) -> t.Callable[P, T]:
        """
        Create and return proxy class for `callback`.
        """
        params = [
            dataclass.Field(param.name, param.default, param.annotation) for param in sigparse.sigparse(callback_)[1:]
        ]

        # This is a python moment.
        class Inner(self.component_type, _dataclass_fields=params, **self.kwargs):  # type: ignore
            async def callback(self, ctx: context.Context):
                kwargs = self._dataclass_values  # type: ignore
                await callback_(ctx, **kwargs)  # type: ignore

        Inner.__name__ = callback_.__name__

        return Inner  # type: ignore

    @property
    @abc.abstractmethod
    def component_type(self) -> type[T]:
        """The component type."""

    @property
    @abc.abstractmethod
    def kwargs(self) -> dict[str, t.Any]:
        """The kwargs for `__init_subclass__`"""


class button(FunctionalComponent[Button]):
    """
    A decorator to create a `flare.Button`. This is a shorthand for when type
    safety is not needed.
    """

    def __init__(
        self,
        cookie: str | None = None,
        label: str | None = None,
        emoji: str | hikari.Emoji | None = None,
        style: hikari.ButtonStyle = hikari.ButtonStyle.PRIMARY,
        disabled: bool = False,
    ) -> None:
        self.cookie = cookie
        self.label = label
        self.emoji = emoji
        self.style = style
        self.disabled = disabled

    @property
    def component_type(self) -> type[Button]:
        return Button

    @property
    def kwargs(self) -> dict[str, t.Any]:
        return {
            "cookie": self.cookie,
            "label": self.label,
            "emoji": self.emoji,
            "style": self.style,
            "disabled": self.disabled,
        }


class select(FunctionalComponent[Select]):
    """
    A decorator to create a `flare.Select`. This is a shorthand for when type
    safety is not needed.
    """

    def __init__(
        self,
        cookie: str | None = None,
        options: t.Sequence[tuple[str, str] | str] | None = None,
        min_values: int | None = None,
        max_values: int | None = None,
        placeholder: hikari.UndefinedOr[str] = hikari.UNDEFINED,
        disabled: bool | None = None,
    ) -> None:
        self.cookie = cookie
        self.options = options
        self.min_values = min_values
        self.max_values = max_values
        self.placeholder = placeholder
        self.disabled = disabled

    @property
    def component_type(self) -> type[Select]:
        return Select

    @property
    def kwargs(self) -> dict[str, t.Any]:
        return {
            "cookie": self.cookie,
            "options": self.options,
            "min_values": self.min_values,
            "max_values": self.max_values,
            "placeholder": self.placeholder,
            "disabled": self.disabled,
        }
