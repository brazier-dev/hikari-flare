from __future__ import annotations

import abc
import copy
import typing as t

import hikari
from typing_extensions import Self

from flare import utils
from flare.components.base import (
    Component,
    SupportsCallback,
    SupportsCookie,
    write_cookie,
)
from flare.dataclass import Dataclass
from flare.exceptions import TitleNotSetError
from flare.internal import bootstrap

if t.TYPE_CHECKING:
    from flare.context import ModalContext


class ModalComponent(Component[hikari.api.ModalActionRowBuilder]):
    @abc.abstractmethod
    def _set_custom_id(self, custom_id: str) -> None:
        ...


class Modal(SupportsCallback["ModalContext"], SupportsCookie, t.MutableSequence[ModalComponent], Dataclass):
    __cookie: t.ClassVar[str]
    __title: t.ClassVar[str | None]

    def __init_subclass__(cls, title: str | None = None, cookie: str | None = None) -> None:
        cls.__title = title
        cls.__cookie = cookie or write_cookie(f"{cls.__name__}.{cls.__module__}")
        bootstrap.components[cls.__cookie] = cls
        super().__init_subclass__()

    def __post_init__(self, _ctx: ModalContext | None = None) -> None:
        self.title = self.__title

        self._components: list[ModalComponent] = []

        # All components are copied so the user can't mutate by accident.
        # This also makes implementing `TextInput.value` on our end easier.
        for attr, value in self._dataclass_values.items():
            if isinstance(value, ModalComponent):
                clone = copy.copy(value)
                setattr(self, attr, clone)
                self._components.append(clone)

        if _ctx:
            for value, component in zip(
                _ctx.values, [component for component in self._components if isinstance(component, TextInput)]
            ):
                component.value = value

        return super().__post_init__()

    @t.overload
    def __getitem__(self, value: int) -> ModalComponent:
        ...

    @t.overload
    def __getitem__(self, value: slice) -> t.MutableSequence[ModalComponent]:
        ...

    def __getitem__(self, value: t.Union[slice, int]) -> t.Union[ModalComponent, t.Sequence[ModalComponent]]:
        return self._components[value]

    def __len__(self) -> int:
        return len(self._components)

    @t.overload
    def __setitem__(self, key: int, value: ModalComponent) -> None:
        ...

    @t.overload
    def __setitem__(self, key: slice, value: t.Iterable[ModalComponent]) -> None:
        ...

    def __setitem__(self, key: int | slice, value: ModalComponent | t.Iterable[ModalComponent]) -> None:
        if isinstance(key, slice):
            self._components[key] = t.cast("t.Iterable[ModalComponent]", value)
        else:
            self._components[key] = t.cast("ModalComponent", value)

    def __delitem__(self, key: int) -> None:
        del self._components[key]

    def insert(self, index: int, value: ModalComponent) -> None:
        self._components.insert(index, value)

    @property
    def cookie(self) -> str:
        return self.__cookie

    def set_title(self, title: str) -> Self:
        self.title = title
        return self

    def build(self) -> list[hikari.api.ModalActionRowBuilder]:
        out: list[hikari.api.ModalActionRowBuilder] = []

        for row_number, component in enumerate(self._components):
            component._set_custom_id(str(row_number))
            row = hikari.impl.ModalActionRowBuilder()
            component.build(row)
            out.append(row)

        return out

    def _without_modal_component(self, d: dict[str, t.Any]) -> dict[str, t.Any]:
        return {
            k: v
            for k, v in d.items()
            if not isinstance(v, ModalComponent) and not utils.any_issubclass(v, ModalComponent)
        }

    async def send(self, inter: hikari.ModalResponseMixin):
        """
        Respond to an iteration with this modal.
        """
        if not self.title:
            raise TitleNotSetError(f"Title for {self.__class__.__name__} not set.")

        custom_id = await bootstrap.active_serde.serialize(
            self.__cookie,
            # `ModalComponent` shouldn't store state so that is removed.
            self._without_modal_component(self._dataclass_annotations),
            self._without_modal_component(self._dataclass_values),
        )
        await inter.create_modal_response(self.title, custom_id, components=self.build())


class TextInput(ModalComponent):
    def __init__(
        self,
        label: str,
        style: hikari.TextInputStyle = hikari.TextInputStyle.SHORT,
        min_length: int | None = None,
        max_length: int | None = None,
        required: bool | None = None,
        value: str | None = None,
        placeholder: str | None = None,
    ) -> None:
        self.label = label
        self.style = style
        self.min_length = min_length
        self.max_length = max_length
        self.required = required
        self.value = value
        self.placeholder = placeholder

        super().__init__()

    @property
    def width(self) -> int:
        """
        The width of the component.
        """
        return 5

    def _set_custom_id(self, custom_id: str):
        self._custom_id = custom_id

    @property
    def custom_id(self) -> str:
        """A custom_id for a component."""
        return self._custom_id

    def set_style(self, style: hikari.TextInputStyle) -> Self:
        self.style = style
        return self

    def set_min_length(self, min_length: int | None) -> Self:
        self.min_length = min_length
        return self

    def set_max_length(self, max_length: int) -> Self:
        self.max_length = max_length
        return self

    def set_required(self, required: bool | None) -> Self:
        self.required = required
        return self

    def set_value(self, value: str | None) -> Self:
        self.value = value
        return self

    def set_placeholder(self, placeholder: str | None) -> Self:
        self.placeholder = placeholder
        return self

    def build(self, action_row: hikari.api.ModalActionRowBuilder) -> None:
        """Build and append a flare component to a hikari action row."""

        action_row.add_text_input(
            self.custom_id,
            self.label,
            style=self.style,
            placeholder=self.placeholder or hikari.UNDEFINED,
            value=self.value or hikari.UNDEFINED,
            required=self.required or True,  # default is True
            min_length=self.min_length or 0,  # default is 0
            max_length=self.max_length or 4000,  # default is 4000
        )


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
