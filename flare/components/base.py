from __future__ import annotations

import abc
import copy
import hashlib
import typing as t

import hikari
import hikari.components

from flare import dataclass
from flare.exceptions import CustomIDNotSetError, SerializerError
from flare.internal import bootstrap

if t.TYPE_CHECKING:
    from flare import row
    from flare.components.button import Button
    from flare.components.select import (
        ChannelSelect,
        MentionableSelect,
        RoleSelect,
        TextSelect,
        UserSelect,
    )
    from flare.context import MessageContext, PartialContext

__all__: t.Final[t.Sequence[str]] = ("Component", "SupportsCookie", "CallbackComponent")

ComponentBuilderT = t.TypeVar("ComponentBuilderT", bound=hikari.api.ComponentBuilder)
PartialContextT = t.TypeVar("PartialContextT", bound="PartialContext[t.Any]", contravariant=True)
P = t.ParamSpec("P")

CallbackComponentT = t.TypeVar("CallbackComponentT", bound="CallbackComponent")


class Component(abc.ABC, t.Generic[ComponentBuilderT]):
    @abc.abstractmethod
    def build(self, action_row: ComponentBuilderT) -> t.Any:
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


class SupportsCallback(t.Protocol[PartialContextT]):
    async def callback(self, ctx: PartialContextT) -> None:
        raise NotImplementedError


def write_cookie(s: str) -> str:
    return hashlib.blake2s(s.encode("latin1"), digest_size=8).digest().decode("latin1")


class CallbackComponent(
    Component[hikari.api.MessageActionRowBuilder],
    SupportsCallback["MessageContext"],
    SupportsCookie,
    dataclass.Dataclass,
):
    """
    An abstract class that all components with callbacks are derive from.
    """

    _cookie: t.ClassVar[str]

    def __init_subclass__(
        cls,
        cookie: str | None = None,
        _dataclass_fields: list[dataclass.Field] | None = None,
    ) -> None:
        super().__init_subclass__(_dataclass_fields)

        cls._cookie = cookie or write_cookie(f"{cls.__name__}.{cls.__module__}")

        bootstrap.components[cls._cookie] = cls

    def __post_init__(self) -> None:
        self._custom_id: str | None = None

    @property
    def custom_id(self) -> str:
        """
        The custom ID of the component.
        """
        if not self._custom_id:
            raise CustomIDNotSetError(f"The row containing `{self.__class__.__name__}` must be awaited.")
        return self._custom_id

    async def set_custom_id(self):
        self._custom_id = await bootstrap.active_serde.serialize(
            self._cookie, self._dataclass_annotations, self._dataclass_values
        )

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
        if not isinstance(component, (hikari.ButtonComponent, hikari.components.SelectMenuComponent)):
            raise SerializerError(f"Flare component type can not be {component.type}")

        assert component.custom_id

        try:
            flare_component, kwargs = await bootstrap.active_serde.deserialize(
                component.custom_id, bootstrap.components
            )
        except SerializerError:
            raise

        component_inst = flare_component(**kwargs)

        if isinstance(component, hikari.ButtonComponent):
            if t.TYPE_CHECKING:
                assert isinstance(component_inst, Button)

            component_inst.set_label(component.label).set_emoji(component.emoji).set_style(
                hikari.ButtonStyle(component.style)
            ).set_disabled(component.is_disabled)
        else:
            if t.TYPE_CHECKING:
                assert isinstance(
                    component_inst, TextSelect | RoleSelect | UserSelect | MentionableSelect | ChannelSelect
                )

            (
                component_inst.set_max_values(component.max_values)
                .set_min_values(component.min_values)
                .set_placeholder(component.placeholder or hikari.UNDEFINED)
                .set_disabled(component.is_disabled)
            )

            if isinstance(component, hikari.components.TextSelectMenuComponent):
                if t.TYPE_CHECKING:
                    assert isinstance(component_inst, TextSelect)

                component_inst.set_options(*((option.label, option.value) for option in component.options))

            if isinstance(component, hikari.components.ChannelSelectMenuComponent):
                if t.TYPE_CHECKING:
                    assert isinstance(component_inst, ChannelSelect)

                component_inst.set_channel_types(*(hikari.ChannelType(c) for c in component.channel_types))

        return component_inst

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
