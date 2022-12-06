import typing as t

import hikari

from flare.context.base import PartialContext

__all__: t.Sequence[str] = ("ModalContext",)


class ModalContext(PartialContext[hikari.ModalInteraction]):
    @property
    def components(self) -> t.Sequence[hikari.ModalActionRowComponent]:
        return self.interaction.components

    @property
    def values(self) -> t.Sequence[str]:
        return [component.value for component in self.components]
