import typing as t

import hikari

from flare.context import Context
from flare.internal.serde import Serde

__all__: t.Final[t.Sequence[str]] = ("install",)

components: dict[str, t.Any] = {}
"""Currently loaded components."""

active_serde: Serde = Serde()
"""The currently active serializer."""


def install(bot: hikari.EventManagerAware, serde: Serde | None = None) -> None:
    """Install flare under the given bot instance.

    Parameters:
        bot:
            The bot to install flare under.
        serde:
            For advanced usage, you can pass a custom serializer. By default uses the default serializer.
    """
    global active_serde

    if serde is not None:
        active_serde = serde

    bot.event_manager.subscribe(hikari.InteractionCreateEvent, _on_inter)


async def _on_inter(event: hikari.InteractionCreateEvent) -> None:
    """
    Function called to respond to an interaction.
    """
    if not isinstance(event.interaction, hikari.ComponentInteraction):
        return

    component, kwargs = active_serde.deserialize(event.interaction.custom_id, components)

    ctx = Context(
        interaction=event.interaction,
    )

    await component.callback(ctx, **kwargs)


# MIT License
#
# Copyright (c) 2022-present Lunarmagpie
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
