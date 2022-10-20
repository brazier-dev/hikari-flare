from __future__ import annotations

import abc
import typing as t

import hikari
import sigparse

from flare import serde
from flare.handle_resp import components

if t.TYPE_CHECKING:
    from flare import context

P = t.ParamSpec("P")


class Component(abc.ABC, t.Generic[P]):
    @abc.abstractmethod
    def build(self, *_: P.args, **kwargs: P.kwargs) -> hikari.api.ActionRowBuilder:
        ...

    @property
    @abc.abstractmethod
    def callback(
        self,
    ) -> t.Callable[t.Concatenate[context.Context, P], t.Awaitable[None]]:
        ...

    @abc.abstractmethod
    async def update_state(
        self, ctx: context.Context, *_: P.args, **kwargs: P.kwargs
    ) -> None:
        ...


class button:
    def __init__(
        self,
        label: str,
        style: hikari.ButtonStyle,
        cookie: str | None = None,
    ) -> None:
        self.label = label
        self.style = style
        self.cookie = cookie

    def __call__(
        self, callback: t.Callable[t.Concatenate[context.Context, P], t.Awaitable[None]]
    ) -> Button[P]:
        return Button(
            callback=callback,
            label=self.label,
            style=self.style,
            cookie=self.cookie,
        )


class Button(Component[P]):
    def __init__(
        self,
        *,
        callback: t.Callable[t.Concatenate[context.Context, P], t.Awaitable[None]],
        label: str,
        style: hikari.ButtonStyle,
        cookie: str | None,
    ) -> None:
        self._callback = callback
        self.label = label
        self.style = style
        self.cookie = cookie or f"{callback.__name__}.{callback.__module__}"

        self.args = {
            param.name: param.annotation for param in sigparse.sigparse(callback)[1:]
        }
        components[self.cookie] = self

    @property
    def callback(
        self,
    ) -> t.Callable[t.Concatenate[context.Context, P], t.Awaitable[None]]:
        return self._callback

    def build(self, *_: P.args, **kwargs: P.kwargs) -> hikari.api.ActionRowBuilder:
        # if not __action_row:
        __action_row = hikari.impl.ActionRowBuilder()
        _id = serde.serialize(self.cookie, self.args, kwargs)

        __action_row.add_button(self.style, _id).set_label(
            self.label
        ).add_to_container()
        return __action_row

    async def update_state(
        self, ctx: context.Context, *_: P.args, **kwargs: P.kwargs
    ) -> None:
        ...
