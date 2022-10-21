from __future__ import annotations

import typing as t

import hikari

from flare.exceptions import FlareException

from .component import Component


class Row(hikari.api.ComponentBuilder, t.MutableSequence[Component[...]]):
    def __init__(self, *components: Component[...]) -> None:
        if (width := sum(component.width for component in components)) > 5:
            raise FlareException(
                f"Row only has space for a combined width of 5 components, got {width}.")

        self._components = list(components)

    @t.overload
    def __getitem__(self, value: int) -> Component[...]:
        ...

    @t.overload
    def __getitem__(self, value: slice) -> t.Sequence[Component[...]]:
        ...

    def __getitem__(self, value: t.Union[slice, int]) -> t.Union[Component[...], t.Sequence[Component[...]]]:
        return self._components[value]

    def __len__(self) -> int:
        return len(self._components)

    def __setitem__(self, key: int, value: Component[...]) -> None:
        if (width := sum(component.width for component in self._components) + value.width) > 5:
            raise FlareException(
                f"Row only has space for a combined width of 5 components, with added component it would be {width}."
            )

        self._components[key] = value

    def __delitem__(self, key: int) -> None:
        del self._components[key]

    def build(self) -> t.MutableMapping[str, t.Any]:
        row = hikari.impl.ActionRowBuilder()

        for component in self._components:
            component.build(row)

        return row.build()

    def insert(self, index: int, value: Component[...]) -> None:
        self._components[index] = value
