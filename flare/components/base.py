from __future__ import annotations

import abc
import copy
import hashlib
import inspect
import typing as t

import hikari
import sigparse

from flare.exceptions import MissingRequiredParameterError, SerializerError
from flare.internal import bootstrap

if t.TYPE_CHECKING:
    from flare import context

__all__: t.Final[t.Sequence[str]] = ("Component", "SupportsCookie", "CallbackComponent")

P = t.ParamSpec("P")

CallbackComponentT = t.TypeVar("CallbackComponentT", bound="CallbackComponent[...]")


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


class CallbackComponent(Component, SupportsCookie, t.Generic[P]):
    """
    An abstract class that all components with callbacks are derive from.
    """

    def __init__(
        self,
        cookie: str | None,
        callback: t.Callable[t.Concatenate[context.Context, P], t.Awaitable[None]],
    ) -> None:
        super().__init__()
        self._custom_id = None
        self._callback = callback
        self._cookie = cookie or hashlib.blake2s(
            f"{callback.__name__}.{callback.__module__}".encode("latin1"), digest_size=8
        ).digest().decode("latin1")

        parameters = sigparse.sigparse(callback)[1:]
        self.args = {param.name: param.annotation for param in parameters}

        if not self.args:
            # If no args were passed, calling set() isn't necessary to construct custom_id.
            self._custom_id = bootstrap.active_serde.serialize(self._cookie, {}, {})
        else:
            # If the function only has optional kwargs, calling set() isn't necessary.
            if all(param.has_default for param in parameters):
                self._custom_id = bootstrap.active_serde.serialize(self._cookie, self.args, {})

        bootstrap.components[self._cookie] = self

    @property
    def custom_id(self) -> str:
        """
        The custom ID of the component.
        """
        if self._custom_id is None:
            raise MissingRequiredParameterError(
                f"Component `{self._callback.__module__}.{self._callback.__name__}` received no"
                f"parameters when it has {len(self.args)}. Did you forget to call `set()`?"
            )
        return self._custom_id

    @property
    def cookie(self) -> str:
        return self.cookie

    @property
    def callback(
        self,
    ) -> t.Callable[t.Concatenate[context.Context, P], t.Awaitable[None]]:
        return self._callback

    @staticmethod
    def from_partial(component: hikari.PartialComponent) -> CallbackComponent[...]:
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
            flare_component, kwargs = bootstrap.active_serde.deserialize(component.custom_id, bootstrap.components)
        except SerializerError:
            raise
        return flare_component.set(kwargs)

    def set(self: CallbackComponentT, *args: P.args, **kwargs: P.kwargs) -> CallbackComponentT:
        new = copy.copy(self)  # Create new instance with params set
        new._custom_id = bootstrap.active_serde.serialize(self._cookie, self.args, self.as_keyword(args, kwargs))
        return new

    def as_keyword(self, args: t.Sequence[t.Any], kwargs: dict[str, t.Any]) -> dict[str, t.Any]:
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
