import typing

import hikari

from flare import serde
from flare.context import Context

_bot = None


def install(bot: hikari.GatewayBot) -> None:
    global _bot
    _bot = bot

    _bot.subscribe(hikari.InteractionCreateEvent, _on_inter)


components: dict[str, typing.Any] = {}


async def _on_inter(event: hikari.InteractionCreateEvent) -> None:
    if event.interaction.type is not hikari.InteractionType.MESSAGE_COMPONENT:
        return

    if typing.TYPE_CHECKING:
        assert isinstance(event.interaction, hikari.ComponentInteraction)

    component, kwargs = serde.deserialize(event.interaction.custom_id, components)

    ctx = Context(
        interaction=event.interaction,
        author=event.interaction.user,
    )

    await component.callback(ctx, **kwargs)
