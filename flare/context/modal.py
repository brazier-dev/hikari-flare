from flare.context.base import PartialContext
import hikari
import typing as t


__all__: t.Sequence[str] = ("ModalContext",)


class ModalContext(PartialContext[hikari.ModalInteraction]):
    @property
    def components(self) -> t.Sequence[hikari.ModalActionRowComponent]:
        return self.interaction.components
