import hikari
from flare.context import Context
import typing
from flare import serde
from flare import converters

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

    cookie, kwargs = serde.deserialize(event.interaction.custom_id, components)
    component = components[cookie]

    ctx = Context(
        interaction=event.interaction,
        author=event.interaction.user,
    )

    await component.callback(ctx, **_cast_kwargs(kwargs, component.args))


def _cast_kwargs(
    kwargs: dict[str, typing.Any], types: dict[str, typing.Any]
) -> dict[str, typing.Any]:
    ret: dict[str, typing.Any] = {}
    for k, v in kwargs.items():
        cast_to = types.get(k)

        if cast_to:
            ret[k] = converters.get_converter(cast_to).from_str(v)
        else:
            ret[k] = v

    return ret
