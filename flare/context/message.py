import typing as t
import hikari

from flare import row

from flare.context.base import PartialContext


__all__: t.Sequence[str] = ("Context",)


class Context(PartialContext[hikari.ComponentInteraction]):
    @property
    def message(self) -> hikari.Message:
        return self._interaction.message

    @property
    def values(self) -> t.Sequence[str]:
        return self.interaction.values

    async def get_components(self) -> t.MutableSequence[row.Row]:
        """Returns the flare components for the interaction this context is proxying"""
        return await row.Row.from_message(self.message)
