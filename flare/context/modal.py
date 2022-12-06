import typing as t

import hikari

from flare.components.modal import ModalComponent, TextInput
from flare.context.base import PartialContext

__all__: t.Sequence[str] = ("ModalContext",)


class ModalContext(PartialContext[hikari.ModalInteraction]):
    @property
    def components(self) -> t.Sequence[hikari.ModalActionRowComponent]:
        return ModalComponent.from_component

    @property
    def values(self) -> t.Sequence[str | None]:
        return [component.value for component in self.components if isinstance(component, TextInput)]
