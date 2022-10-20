import abc
import hikari
import typing
import sigparse

from flare.handle_resp import _components
from flare import typedefs
from flare import id

ButtonSelf = typing.TypeVar("ButtonSelf", bound="button")


class Component(abc.ABC):
    @abc.abstractmethod
    def build(self, __action_row: hikari.api.ActionRowBuilder | None = None, **kwargs: typing.Any) -> hikari.api.ActionRowBuilder:
        ...


class button(Component):
    def __init__(self, *, label: str, style: hikari.ButtonStyle, cookie: str | None = None) -> None:
        self.callback: typedefs.ComponentCallbackT | None = None
        self.label = label
        self.style = style
        self.cookie = cookie

        self._args: dict[str, sigparse.Parameter] | None = None

    @property
    def args(self) -> dict[str, typing.Any]:
        assert self._args is not None
        return self._args

    def __call__(self: ButtonSelf, callback: typedefs.ComponentCallbackT) -> ButtonSelf:
        self.callback = callback

        self._args = {
            param.name:param.annotation for param in sigparse.sigparse(callback)[1:]
        }

        if not self.cookie:
            self.cookie = f"{callback.__name__}.{callback.__module__}"

        _components[self.cookie] = self

        return self

    def build(self, __action_row: hikari.api.ActionRowBuilder | None = None, **kwargs: typing.Any) -> hikari.api.ActionRowBuilder:
        if not __action_row:
            __action_row = hikari.impl.ActionRowBuilder()

        assert self.cookie
        _id = id.serialize(self.cookie, self.args, kwargs)

        __action_row.add_button(
            self.style, _id
        ).set_label(self.label).add_to_container()
        return __action_row
