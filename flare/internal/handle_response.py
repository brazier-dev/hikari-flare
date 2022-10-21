import typing

import hikari

from flare.context import Context
from flare.internal import serde


def install(bot: hikari.GatewayBot) -> None:
    bot.subscribe(hikari.InteractionCreateEvent, _on_inter)


components: dict[str, typing.Any] = {}


async def _on_inter(event: hikari.InteractionCreateEvent) -> None:
    """
    Function called to respond to an interaction.
    """
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
