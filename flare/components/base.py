from __future__ import annotations

import abc
import copy
import typing as t

import hikari
import sigparse

from flare.exceptions import MissingRequiredParameterError
from flare.internal import event_handler, serde

if t.TYPE_CHECKING:
    from flare import context

__all__: t.Final[t.Sequence[str]] = ("Component",)

P = t.ParamSpec("P")

ComponentT = t.TypeVar("ComponentT", bound="Component[...]")


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
            # If no args were passed, calling set() isn't necessary to construct custom_id
            self._custom_id = self.cookie

        event_handler.components[self.cookie] = self

    @property
    @abc.abstractmethod
    def width(self) -> int:
        """
        The width of the component.
        """
        ...

    @property
    def custom_id(self) -> str:
        """
        The custom ID of the component.
        """
        if self._custom_id is None:
            raise MissingRequiredParameterError(
                f"Component {self.cookie} received no parameters when it has {len(self.args)}. Did you forget to call `set()`?"
            )
        return self._custom_id

    @property
    def callback(
        self,
    ) -> t.Callable[t.Concatenate[context.Context, P], t.Awaitable[None]]:
        return self._callback

    def set(self: ComponentT, *_: P.args, **values: P.kwargs) -> ComponentT:
        new = copy.copy(self)  # Create new instance with params set
        new._custom_id = serde.serialize(self.cookie, self.args, values)
        return new

    @abc.abstractmethod
    def build(self, action_row: hikari.api.ActionRowBuilder) -> None:
        """Build and append a flare component to a hikari action row."""
        ...

    @abc.abstractclassmethod
    def from_partial(cls: ComponentT, partial: hikari.PartialComponent) -> ComponentT | None:
        """
        Convert a hikari partial component to a flare component.
        This only works if the component was previously created with flare, otherwise it will return `None`.
        """
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
