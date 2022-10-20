import hikari
from flare.context import Context
import typing
from flare import id

_bot = None

def install(bot: hikari.GatewayBot) -> None:
    global _bot
    _bot = bot

    _bot.subscribe(hikari.InteractionCreateEvent, _on_inter)

_components: dict[str, typing.Any] = {}

async def _on_inter(event: hikari.InteractionCreateEvent) -> None:
    if event.interaction.type is not hikari.InteractionType.MESSAGE_COMPONENT:
        return

    assert isinstance(event.interaction, hikari.ComponentInteraction)

    cookie, kwargs = id.deserialize(event.interaction.custom_id, _components)

    ctx = Context(
        interaction=event.interaction,
        author=event.interaction.user,
    )

    await _components[cookie].callback(ctx, **kwargs)
