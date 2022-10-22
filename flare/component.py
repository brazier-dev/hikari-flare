from __future__ import annotations

import abc
import inspect
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

    def set(self, *args: P.args, **values: P.kwargs) -> Component[P]:
        new = copy.copy(self)  # Create new instance with params set
        new._custom_id = serde.serialize(self.cookie, self.args, self.as_keyword(args, values))
        return new

    @abc.abstractmethod
    def build(self, action_row: hikari.api.ActionRowBuilder) -> None:
        """Build and append a flare component to a hikari action row."""
        ...

    @abc.abstractmethod
    async def update_state(self, ctx: context.Context, *_: P.args, **kwargs: P.kwargs) -> None:
        ...

    def as_keyword(self, args: list[t.Any], kwargs: dict[str, t.Any]) -> dict[str, t.Any]:
        """
        Convert arguments and keyword arguments in a dictionary of keyword
        arguments. This is done to make serialization and deserialization easier
        because the differences between `POSITIONAL_OR_KEYWORD` and
        `KEYWORD_ONLY` don't need to be considered.
        """
        out: dict[str, t.Any] = {}

        pos_or_kw: list[sigparse.Parameter] = []

        for arg in sigparse.sigparse(self.callback)[1:]:
            match arg.kind:
                case inspect._ParameterKind.POSITIONAL_OR_KEYWORD:
                    pos_or_kw.append(arg)
                case inspect._ParameterKind.KEYWORD_ONLY:
                    # Arguments are considered `KEYWORD_ONLY` if they are not
                    # `POSITIONAL_OR_KEYWORD`.
                    pass
                case inspect._ParameterKind.POSITIONAL_ONLY:
                    raise NotImplementedError("Positional only arguments are not supported for component callbacks")
                case inspect._ParameterKind.VAR_POSITIONAL:
                    raise NotImplementedError("`*args` is not supported for component callbacks.")
                case inspect._ParameterKind.VAR_KEYWORD:
                    raise NotImplementedError("`**kwargs` is not supported for component callbacks.")

        for arg, value in zip(pos_or_kw, args):
            out[arg.name] = value

        return out | kwargs


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

    async def update_state(self, ctx: context.Context, *_: P.args, **kwargs: P.kwargs) -> None:
        ...


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
