import logging

import hikari

from flare.components import CallbackComponent, Modal
from flare.context import MessageContext, ModalContext
from flare.exceptions import SerializerError
from flare.internal import bootstrap

logger = logging.getLogger(__name__)


async def on_inter(event: hikari.InteractionCreateEvent) -> None:
    """
    Function called to respond to an interaction.
    """
    if not isinstance(event.interaction, (hikari.ComponentInteraction, hikari.ModalInteraction)):
        return

    try:
        component, kwargs = await bootstrap.active_serde.deserialize(event.interaction.custom_id, bootstrap.components)
    except SerializerError:  # If the custom_id is invalid, it was probably not created by flare.
        logger.debug(
            f"Flare received custom_id '{event.interaction.custom_id}' which it cannot deserialize.", exc_info=True
        )
        return

    if isinstance(event.interaction, hikari.ComponentInteraction):
        ctx = MessageContext(
            interaction=event.interaction,
        )
        assert issubclass(component, CallbackComponent)
        await component(**kwargs).callback(ctx)
    else:
        ctx = ModalContext(interaction=event.interaction)
        assert issubclass(component, Modal)
        await component(**kwargs, _ctx=ctx).callback(ctx)  # type: ignore


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
