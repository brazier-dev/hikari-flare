from __future__ import annotations

import typing as t

import hikari
from typing_extensions import Self

from flare import dataclass
from flare.components.base import CallbackComponent, Component
from flare.components.functional import FunctionalComponent
from flare.exceptions import ComponentError

__all__: t.Sequence[str] = ("Button", "button", "LinkButton")

P = t.ParamSpec("P")
ButtonT = t.TypeVar("ButtonT", bound="Button")


class Button(CallbackComponent):
    __label: t.ClassVar[str | None]
    __emoji: t.ClassVar[hikari.Emoji | str | None]
    __style: t.ClassVar[hikari.ButtonStyle]
    __disabled: t.ClassVar[bool]

    def __init_subclass__(
        cls,
        *,
        label: str | None = None,
        emoji: hikari.Emoji | str | None = None,
        style: hikari.ButtonStyle = hikari.ButtonStyle.PRIMARY,
        disabled: bool = False,
        cookie: str | None = None,
        _dataclass_fields: list[dataclass.Field] | None = None,
    ) -> None:
        super().__init_subclass__(cookie, _dataclass_fields)
        cls.__label = label
        cls.__emoji = emoji
        cls.__style = style
        cls.__disabled = disabled

    def __post_init__(self):
        super().__post_init__()
        self.label = self.__label
        self.emoji = self.__emoji
        self.style = self.__style
        self.disabled = self.__disabled

    @property
    def width(self) -> int:
        return 1

    def set_label(self, label: str | None) -> Self:
        self.label = label
        return self

    def set_emoji(self, emoji: hikari.Emoji | str | None) -> Self:
        self.emoji = emoji
        return self

    def set_style(self, style: hikari.ButtonStyle) -> Self:
        self.style = style
        return self

    def set_disabled(self, disabled: bool) -> Self:
        self.disabled = disabled
        return self

    def build(self, action_row: hikari.api.MessageActionRowBuilder) -> None:
        """
        Build the button into the passed action row.
        """

        if self.style == hikari.ButtonStyle.LINK:
            raise ComponentError("Link buttons are not supported.")

        if not self.label and not self.emoji:
            raise ComponentError(f"Label and emoji cannot both be empty for button component {self.cookie}.")

        button = action_row.add_button(self.style, self.custom_id)

        if self.label:
            button.set_label(self.label)

        emoji: hikari.Emoji | hikari.UndefinedType
        if isinstance(self.emoji, str):
            emoji = hikari.Emoji.parse(self.emoji)
        else:
            emoji = self.emoji or hikari.UNDEFINED

        if self.emoji:
            button.set_emoji(emoji)

        button.set_is_disabled(self.disabled)

        button.add_to_container()


class button(FunctionalComponent[Button]):
    """
    A decorator to create a `flare.Button`. This is a shorthand for when type
    safety is not needed.
    """

    def __init__(
        self,
        *,
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


class LinkButton(Component[hikari.api.MessageActionRowBuilder]):
    """
    A button with a link.

    Args:
        url:
            The link for this button.
        label:
            The label on the button.
        emoji:
            The emoji on the button.
    """

    @t.overload
    def __init__(
        self,
        url: str,
        *,
        label: str,
    ) -> None:
        ...

    @t.overload
    def __init__(
        self,
        url: str,
        *,
        emoji: hikari.Emoji,
    ) -> None:
        ...

    @t.overload
    def __init__(
        self,
        url: str,
        *,
        label: str,
        emoji: hikari.Emoji,
    ) -> None:
        ...

    def __init__(
        self,
        url: str,
        *,
        label: str | None = None,
        emoji: hikari.Emoji | None = None,
    ) -> None:
        self.url = url
        self.label = label
        self.emoji = emoji

    @property
    def width(self) -> int:
        return 1

    @property
    def custom_id(self) -> str:
        return self.url

    def build(self, action_row: hikari.api.MessageActionRowBuilder) -> None:
        button = action_row.add_button(hikari.ButtonStyle.LINK, self.url)

        if self.label:
            button.set_label(self.label)

        if self.emoji:
            button.set_emoji(self.emoji)

        button.add_to_container()


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
