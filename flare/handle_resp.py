import hikari
from flare.context import Context
import typing
import sigparse
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
    component = _components[cookie]

    ctx = Context(
        interaction=event.interaction,
        author=event.interaction.user,
    )

    await component.callback(ctx, **_cast_kwargs(kwargs, component.args))

def _cast_kwargs(kwargs: dict[str, typing.Any], types: dict[str, typing.Any]) -> dict[str, typing.Any]:
    ret = {}
    for k, v in kwargs.items():
        cast_to = types.get(k)
        if cast_to:
            ret[k] = typing.get_args(cast_to)[0](v)
        else:
            ret[k] = v

    return ret
