import itertools
import typing as t

import hikari

from flare import row
from flare.context.base import PartialContext

__all__: t.Sequence[str] = ("MessageContext",)


class MessageContext(PartialContext[hikari.ComponentInteraction]):
    @property
    def message(self) -> hikari.Message:
        """The message this context is proxying."""
        return self._interaction.message

    @property
    def values(self) -> t.Sequence[str]:
        """The values selected for a select menu."""
        return self.interaction.values

    @property
    def users(self) -> t.Sequence[hikari.User]:
        """The users selected for a user select menu."""
        if not self.interaction.resolved:
            return []

        return list(self.interaction.resolved.users.values())

    @property
    def roles(self) -> t.Sequence[hikari.Role]:
        """The values selected for a role select menu."""
        if not self.interaction.resolved:
            return []

        return list(self.interaction.resolved.roles.values())

    @property
    def mentionables(self) -> t.Sequence[hikari.User | hikari.Role]:
        """The values selected for a mentionable select menu."""
        if not self.interaction.resolved:
            return []

        return list(
            itertools.chain(
                self.interaction.resolved.users.values(),
                self.interaction.resolved.roles.values(),
            )
        )

    @property
    def channels(self) -> t.Sequence[hikari.PartialChannel]:
        """The values selected for a channel select menu."""
        if not self.interaction.resolved:
            return []

        return list(self.interaction.resolved.channels.values())

    async def get_components(self) -> t.MutableSequence[row.Row]:
        """Returns the flare components for the interaction this context is proxying"""
        return await row.Row.from_message(self.message)


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
