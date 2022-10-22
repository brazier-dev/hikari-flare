from __future__ import annotations

import typing as t

import hikari

from flare.components.base import Component
from flare.exceptions import ComponentError, SerializerError
from flare.internal import serde
from flare.internal.event_handler import components as _components

if t.TYPE_CHECKING:
    from flare import context

__all__: t.Final[t.Sequence[str]] = ("button", "Button")

P = t.ParamSpec("P")
ComponentT = t.TypeVar("ComponentT", bound="Component[...]")


class button:
    """
    Decorator for a button message component.

    Args:
        label:
            The label on the button.
        style:
            The button style.
        cookie:
            An identifier to use for the button. A custom cookie can be supplied so
            a shorter one is used in serializing and deserializing.
        disabled:
            Whether the button is disabled.
        emoji:
            The emoji on the button.
    """

    def __init__(
        self,
        label: str | None,
        emoji: hikari.Emoji | str | None,
        style: hikari.ButtonStyle,
        disabled: bool = False,
        cookie: str | None = None,
    ) -> None:
        self.label = label
        self.emoji = emoji
        self.disabled = disabled
        self.style = style
        self.cookie = cookie

    def __call__(self, callback: t.Callable[t.Concatenate[context.Context, P], t.Awaitable[None]]) -> Button[P]:
        return Button(
            callback=callback,
            label=self.label,
            emoji=self.emoji,
            disabled=self.disabled,
            style=self.style,
            cookie=self.cookie,
        )


class Button(Component[P]):
    def __init__(
        self,
        *,
        callback: t.Callable[t.Concatenate[context.Context, P], t.Awaitable[None]],
        label: str | None,
        emoji: hikari.Emoji | str | None,
        style: hikari.ButtonStyle,
        disabled: bool = False,
        cookie: str | None,
    ) -> None:
        super().__init__(cookie, callback)
        self.label = label
        self.emoji = emoji
        self.style = style
        self.disabled = disabled

        if isinstance(self.emoji, str):
            self.emoji = hikari.Emoji.parse(self.emoji)

    @property
    def width(self) -> int:
        return 1

    def build(self, action_row: hikari.api.ActionRowBuilder) -> None:
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

        if self.emoji:
            button.set_emoji(self.emoji)

        button.set_is_disabled(self.disabled)

        button.add_to_container()

    @classmethod
    def from_partial(cls, partial: hikari.PartialComponent) -> Button[P] | None:
        if not partial.type == hikari.ComponentType.BUTTON:
            raise TypeError("Partial component is not a button.")
        assert isinstance(partial, hikari.ButtonComponent)

        if not partial.custom_id:
            raise ValueError("Partial component is missing custom_id.")
        try:
            component, kwargs = serde.deserialize(partial.custom_id, _components)
        except SerializerError:
            return None

        assert isinstance(component, cls)
        component = component.set(**kwargs) # type: ignore reportGeneralTypeIssues
        return component


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
