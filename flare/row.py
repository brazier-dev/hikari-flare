from __future__ import annotations

import typing as t

import hikari

from flare.components import CallbackComponent, Component, LinkButton
from flare.exceptions import RowMaxWidthError, SerializerError
from flare.utils import gather_iter


class Row(hikari.api.ComponentBuilder, t.MutableSequence[Component[hikari.api.MessageActionRowBuilder]]):
    def __init__(self, *components: Component[hikari.api.MessageActionRowBuilder]) -> None:
        if (width := sum(component.width for component in components)) > 5:
            raise RowMaxWidthError(f"Row only has space for a combined width of 5 components, got {width}.")

        self._components = list(components)

    def __check_width(self, value: Component[hikari.api.MessageActionRowBuilder]):
        if (width := sum(component.width for component in self._components) + value.width) > 5:
            raise RowMaxWidthError(
                f"Row only has space for a combined width of 5 components, with added component it would be {width}."
            )

    @t.overload
    def __getitem__(self, value: int) -> Component[hikari.api.MessageActionRowBuilder]:
        ...

    @t.overload
    def __getitem__(self, value: slice) -> t.MutableSequence[Component[hikari.api.MessageActionRowBuilder]]:
        ...

    def __getitem__(
        self, value: t.Union[slice, int]
    ) -> t.Union[
        Component[hikari.api.MessageActionRowBuilder], t.Sequence[Component[hikari.api.MessageActionRowBuilder]]
    ]:
        return self._components[value]

    def __len__(self) -> int:
        return len(self._components)

    def __setitem__(self, key: int, value: Component[hikari.api.MessageActionRowBuilder]) -> None:
        self.__check_width(value)
        self._components[key] = value

    def __delitem__(self, key: int) -> None:
        del self._components[key]

    def __await__(self):
        async def set_custom_ids() -> Row:
            for component in self._components:
                if isinstance(component, CallbackComponent):
                    await component.set_custom_id()
            return self

        return set_custom_ids().__await__()

    @classmethod
    async def __gather_rows(cls, action_row: hikari.MessageActionRowComponent) -> Row:
        return Row(*await gather_iter(cls.__gather_components(components) for components in action_row))

    @staticmethod
    async def __gather_components(component: hikari.PartialComponent):
        if isinstance(component, hikari.ButtonComponent) and component.style is hikari.ButtonStyle.LINK:
            assert component.url

            if not (component.label or component.emoji):
                raise SerializerError("Link button does not have label or emoji.")
            # This is a valid overload users shouldn't be able to use.
            return LinkButton(
                url=component.url,
                label=component.label,  # type: ignore
                emoji=component.emoji,  # type: ignore
            )
        else:
            return await CallbackComponent.from_partial(component)

    @classmethod
    async def from_message(cls, message: hikari.Message) -> t.MutableSequence[Row]:
        """Create a row from a message's components.

        Args:
            message:
                The message to create the row from.

        Returns:
            Row:
                The created rows from the message's components.
        """
        return await gather_iter(cls.__gather_rows(action_row) for action_row in message.components)

    def build(self) -> t.MutableMapping[str, t.Any]:
        row = hikari.impl.MessageActionRowBuilder()

        for component in self._components:
            component.build(row)

        return row.build()

    def insert(self, index: int, value: Component[hikari.api.MessageActionRowBuilder]) -> None:
        self.__check_width(value)
        self._components.insert(index, value)
