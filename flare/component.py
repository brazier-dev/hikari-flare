from __future__ import annotations

import abc
import copy
import typing as t

import hikari
import sigparse

from flare.exceptions import ComponentError, MissingRequiredParameterError
from flare.internal import event_handler, serde

if t.TYPE_CHECKING:
    from flare import context

P = t.ParamSpec("P")

__all__: t.Final[t.Sequence[str]] = ("Component", "button", "Button")

Self = t.TypeVar("Self", bound="Component[...]")


class Component(abc.ABC, t.Generic[P]):
    """
    An abstract class that all components derive from.
    """

    def __init__(
        self,
        cookie: str | None,
        callback: t.Callable[t.Concatenate[context.Context, P], t.Awaitable[None]],
    ) -> None:
        self._custom_id = None
        self._callback = callback
        self.cookie = cookie or f"{callback.__name__}.{callback.__module__}"

        self.args = {param.name: param.annotation for param in sigparse.sigparse(callback)[1:]}

        if not self.args:
            # If no args were passed, calling with_params isn't necessary to construct custom_id
            self._custom_id = self.cookie

        event_handler.components[self.cookie] = self

    @property
    def width(self) -> int:
        """
        The width of the component.
        """
        return 1

    @property
    def custom_id(self) -> str:
        """
        The custom ID of the component.
        """
        if self._custom_id is None:
            raise MissingRequiredParameterError(
                f"Component received no parameters when it has {len(self.args)}. Did you forget to call `with_params()`?"
            )
        return self._custom_id

    @property
    def callback(
        self,
    ) -> t.Callable[t.Concatenate[context.Context, P], t.Awaitable[None]]:
        return self._callback

    def set(self: Self, *_: P.args, **values: P.kwargs) -> Self:
        new = copy.copy(self)  # Create new instance with params set
        new._custom_id = serde.serialize(self.cookie, self.args, values)
        return new

    @abc.abstractmethod
    def build(self, action_row: hikari.api.ActionRowBuilder) -> None:
        """Build and append a flare component to a hikari action row."""
        ...


class button:
    """
    A button message component.

    Args:
        label:
            The label on the button.
        style:
            The button style.
        cookie:
            An identifier to use for the button. A custom cookie can be supplied so
            a shorter one is used in serializing and deserializing.
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

    def build(self, action_row: hikari.api.ActionRowBuilder) -> None:
        """
        Build the button into the passed action row.
        """

        if self.style == hikari.ButtonStyle.LINK:
            raise ComponentError("Link buttons are not supported.")

        if not self.label and not self.emoji:
            raise ComponentError("Label and emoji cannot both be empty for button component.")

        button = action_row.add_button(self.style, self.custom_id)

        if self.label:
            button.set_label(self.label)

        if self.emoji:
            button.set_emoji(self.emoji)

        button.set_is_disabled(self.disabled)

        button.add_to_container()


class select:
    """
    A select menu message component.

    Args:
        options:
            An array of options for the select menu. This must be provided when
            the class is created or using `SelectMenu.set_options`.
        min_vales:
            The minimum amount of values a user must select.
        max_values:
            The maximum amount of values a user must select.
        placeholder:
            Placeholder text when no option is selected.
        disabled:
            Whether the button is disabled.
        cookie:
            An identifier to use for the select menu. A custom cookie can be
            supplied so a shorter one is used in serializing and deserializing.
    """

    def __init__(
        self,
        options: t.Sequence[tuple[str, str] | str] | None = None,
        min_values: int = 1,
        max_values: int = 1,
        placeholder: hikari.UndefinedOr[str] = hikari.UNDEFINED,
        disabled: bool = False,
        cookie: str | None = None,
    ) -> None:
        self.cookie = cookie
        self.options = options
        self.min_values = min_values
        self.max_values = max_values
        self.placeholder = placeholder
        self.disabled = disabled

    def __call__(self, callback: t.Callable[t.Concatenate[context.Context, P], t.Awaitable[None]]) -> SelectMenu[P]:
        return SelectMenu(
            cookie=self.cookie,
            callback=callback,
            options=self.options,
            min_values=self.min_values,
            max_values=self.max_values,
            placeholder=self.placeholder,
            disabled=self.disabled,
        )


class SelectMenu(Component[P]):
    def __init__(
        self,
        cookie: str | None,
        callback: t.Callable[t.Concatenate[context.Context, P], t.Awaitable[None]],
        options: t.Sequence[tuple[str, str] | str] | None,
        min_values: int,
        max_values: int,
        placeholder: hikari.UndefinedOr[str],
        disabled: bool,
    ) -> None:
        super().__init__(cookie, callback)
        self.options = options
        self.min_values = min_values
        self.max_values = max_values
        self.placeholder = placeholder
        self.disabled = disabled

    @property
    def width(self) -> int:
        """
        The width of the component.
        """
        return 5

    def set(self, *_: P.args, **values: P.kwargs) -> SelectMenu[P]:
        s = super().set(*_, **values)
        # The options array should be different for clones.
        s.options = copy.copy(self.options)
        return s

    def set_options(self, *options: tuple[str, str] | str) -> None:
        self.options = options

    def build(self, action_row: hikari.api.ActionRowBuilder) -> None:
        """
        Build the select menu into the passed in action row.
        """
        select = action_row.add_select_menu(self.custom_id)

        if self.options:
            for option in self.options:
                if isinstance(option, str):
                    select.add_option(option, option).add_to_menu()
                else:
                    select.add_option(*option).add_to_menu()
        else:
            raise ComponentError("Expected one or more options for select menu. Got zero.")

        if self.min_values > len(self.options):
            raise ComponentError("Cannot create a select menu with greater min options than options.")
        if self.max_values < len(self.options):
            raise ComponentError("Cannot create a select menu with less max options than options.")

        select.set_min_values(self.min_values)
        select.set_max_values(self.max_values)
        select.set_placeholder(self.placeholder)
        select.set_is_disabled(self.disabled)
        select.add_to_container()


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
