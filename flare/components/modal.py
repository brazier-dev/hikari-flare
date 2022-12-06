import abc
import typing as t

import hikari

from flare.internal import bootstrap
from flare.dataclass import Dataclass
from flare.components.base import SupportsCallback, Component, SupportsCookie, write_cookie
from flare import utils


class Modal(SupportsCallback, SupportsCookie, Dataclass):
    __cookie: t.ClassVar[str]
    __title: t.ClassVar[str]

    def __init_subclass__(cls, title: str, cookie: str | None = None) -> None:
        cls.__title = title
        cls.__cookie = cookie or write_cookie(f"{cls.__name__}.{cls.__module__}")
        bootstrap.components[cls.__cookie] = cls
        super().__init_subclass__()

    def __post_init__(self) -> None:
        self.title = self.__title
        return super().__post_init__()

    @property
    def cookie(self) -> str:
        return self.__cookie

    def set_title(self, title: str) -> None:
        self.title = title

    def build(self) -> list[hikari.api.ModalActionRowBuilder]:
        out: list[hikari.api.ModalActionRowBuilder] = []

        row_number = 0
        for component in self._dataclass_values.values():
            if not isinstance(component, ModalComponent):
                continue
            component.set_custom_id(str(row_number))
            row = hikari.impl.ModalActionRowBuilder()
            component.build(row)
            out.append(row)
            row_number += 1

        return out

    def _without_modal_component(self, d: dict[str, t.Any]) -> dict[str, t.Any]:
        return {
            k: v
            for k, v in d.items()
            if not isinstance(v, ModalComponent) and not utils.any_issubclass(v, ModalComponent)
        }

    async def send(self, inter: hikari.CommandInteraction):
        custom_id = await bootstrap.active_serde.serialize(
            self.__cookie,
            self._without_modal_component(self._dataclass_annotations),
            self._without_modal_component(self._dataclass_values),
        )
        await inter.create_modal_response(self.title, custom_id, components=self.build())


class ModalComponent(Component[hikari.api.ModalActionRowBuilder]):
    @abc.abstractmethod
    def set_custom_id(self, custom_id: str) -> None:
        ...


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

    def set_custom_id(self, custom_id: str):
        self._custom_id = custom_id

    @property
    def custom_id(self) -> str:
        """A custom_id for a component."""
        return self._custom_id

    def build(self, action_row: hikari.api.ModalActionRowBuilder) -> None:
        """Build and append a flare component to a hikari action row."""
        text_input = action_row.add_text_input(custom_id=self.custom_id, label=self.label)

        if self.style:
            text_input.set_style(self.style)

        if self.min_length is not None:
            text_input.set_min_length(self.min_length)

        if self.max_length is not None:
            text_input.set_max_length(self.max_length)

        if self.required is not None:
            text_input.set_required(self.required)

        if self.value is not None:
            text_input.set_value(self.value)

        if self.placeholder is not None:
            text_input.set_placeholder(self.placeholder)

        text_input.add_to_container()
        text_input.build()
