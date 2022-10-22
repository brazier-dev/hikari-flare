import typing as t

import hikari

from flare.internal.serde import Serde, SerdeABC

__all__: t.Final[t.Sequence[str]] = ("install",)


components: dict[str, t.Any] = {}
"""Currently loaded components."""

active_serde: SerdeABC = Serde()
"""The currently active serializer."""


def install(bot: hikari.EventManagerAware, serde: SerdeABC | None = None) -> None:
    """Install flare under the given bot instance.

    Args:
        bot:
            The bot to install flare under.
        serde:
            For advanced usage, you can pass a custom serializer. By default uses the default serializer.
    """
    global active_serde

    if serde is not None:
        active_serde = serde

    from flare.internal.event_handler import on_inter

    bot.event_manager.subscribe(hikari.InteractionCreateEvent, on_inter)
