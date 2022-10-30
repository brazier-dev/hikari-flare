from __future__ import annotations

import abc
import copy
import dataclasses
import hashlib
import typing as t
from typing_extensions import dataclass_transform

import hikari
import sigparse

from flare.exceptions import SerializerError
from flare.internal import bootstrap

if t.TYPE_CHECKING:
    from flare import context, row

__all__: t.Final[t.Sequence[str]] = ("Component", "SupportsCookie", "CallbackComponent")

P = t.ParamSpec("P")

CallbackComponentT = t.TypeVar("CallbackComponentT", bound="CallbackComponent")


class Component(abc.ABC):
    @abc.abstractmethod
    def build(self, action_row: hikari.api.ActionRowBuilder) -> None:
        """Build and append a flare component to a hikari action row."""
        ...

    @property
    @abc.abstractmethod
    def width(self) -> int:
        """
        The width of the component.
        """
        ...

    @property
    @abc.abstractmethod
    def custom_id(self) -> str:
        """A custom_id for a component."""
        ...


class SupportsCookie(abc.ABC):
    @property
    @abc.abstractmethod
    def cookie(self) -> str:
        """A unique identifier for a component."""
        ...


class SupportsCallback(t.Protocol):
    async def callback(self, ctx: context.Context) -> None:
        raise NotImplementedError


@dataclass_transform()
class CallbackComponent(Component, SupportsCookie, SupportsCallback):
    """
    An abstract class that all components with callbacks are derive from.
    """

    _custom_id: str | None
    _cookie: t.ClassVar[str]
    _class_vars: t.ClassVar[dict[str, t.Any]]

    def __init_subclass__(
        cls,
        cookie: str | None = None,
    ) -> None:
        cls = dataclasses.dataclass(cls)

        cls._custom_id = None
        cls._cookie = cookie or hashlib.blake2s(
            f"{cls.__name__}.{cls.__module__}".encode("latin1"), digest_size=8
        ).digest().decode("latin1")

        cls._class_vars: dict[str, t.Any] = {
            class_var.name: class_var.annotation
            for class_var in sigparse.classparse(cls)
            if not class_var.name.startswith("_")
        }

        bootstrap.components[cls._cookie] = cls

    @property
    def custom_id(self) -> str:
        """
        The custom ID of the component.
        """
        if not self._custom_id:
            raise Exception
        return self._custom_id

    async def set_custom_id(self):
        self._custom_id = await bootstrap.active_serde.serialize(self._cookie, self._class_vars, self.kw_args)

    @property
    def cookie(self) -> str:
        return self._cookie

    @staticmethod
    async def from_partial(component: hikari.PartialComponent) -> CallbackComponent:
        """
        Build a flare component from `hikari.PartialComponent`.

        Args:
            component:
                A partial component. The component type must be `hikari ComponentType.BUTTON`
                or `hikari.ComponentType.SELECT_MENU`.

        Returns:
            A component.

        Raises:
            SerializerError: The component could not be deserialized.
        """
        if not isinstance(component, (hikari.ButtonComponent, hikari.SelectMenuComponent)):
            raise SerializerError(f"Flare component type can not be {component.type}")

        assert component.custom_id

        try:
            flare_component, kwargs = await bootstrap.active_serde.deserialize(
                component.custom_id, bootstrap.components
            )
        except SerializerError:
            raise
        return flare_component(**kwargs)  # type: ignore

    def _clone(self: CallbackComponentT) -> CallbackComponentT:
        return copy.copy(self)

    def get_from(self: CallbackComponentT, rows: t.Sequence[row.Row]) -> t.Sequence[CallbackComponentT]:
        """
        Return all instances of this component that appear in :class:`typing.Sequence[flare.row.Row]`.

        Args:
            rows:
                The rows to search through.
        Returns:
            A list of all components of this type that appear in ``rows``.

        """
        out: list[CallbackComponentT] = []
        for row in rows:
            for component in row:
                if isinstance(component, type(self)) and component.cookie == self.cookie:
                    out.append(component)
        return out

    def set_in(
        self: CallbackComponentT, rows: t.Sequence[row.Row], *args: t.Any, **kwargs: t.Any
    ) -> t.Sequence[CallbackComponentT]:
        """
        Edit all instances of this component in-place in :class:`typing.Sequence[flare.row.Row]`.

        .. code-block:: python

            import flare

            @flare.button(label="Click me!")
            async def counter_button(
                ctx: flare.Context,
                n: int = 0,
            ) -> None:
                rows = ctx.get_components()
                # Edit this button in the array `rows`
                counter_button.set_in(rows, n=n+1)
                await ctx.edit_response(
                    # Rows must be passed back into `edit_response`
                    components=rows,
                )

        Args:
            rows:
                The rows to edit.
        Returns:
            A list of all components of this type that appear in `rows`.
        """
        mes = self.get_from(rows)
        for me in mes:
            me._change_params(*args, **kwargs)
        return mes

    @property
    def kw_args(self) -> dict[str, t.Any]:
        return dataclasses.asdict(self)


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
