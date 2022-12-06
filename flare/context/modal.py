import typing as t

import hikari

from flare.context.base import PartialContext

__all__: t.Sequence[str] = ("ModalContext",)


class ModalContext(PartialContext[hikari.ModalInteraction]):
    @property
    def components(self) -> t.Sequence[hikari.ModalActionRowComponent]:
        return self.interaction.components

    @property
    def values(self) -> t.Sequence[str | None]:
        # This is type safe. Not sure why the type checker doesn't understand that.
        return [row[0].value for row in self.components if isinstance(row[0], hikari.TextInputComponent)]  # type: ignore
