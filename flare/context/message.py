import typing as t

import hikari

from flare import row
from flare.context.base import PartialContext
from flare import mentionable

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
        users: list[hikari.User] = []

        if not self.interaction.resolved:
            return []

        for value in self.interaction.resolved.users.values():
            users.append(value)

        return users

    @property
    def roles(self) -> t.Sequence[hikari.Role]:
        """The values selected for a role select menu."""
        roles: list[hikari.Role] = []

        if not self.interaction.resolved:
            return []

        for value in self.interaction.resolved.roles.values():
            roles.append(value)

        return roles

    @property
    def mentionables(self) -> t.Sequence[mentionable.Mentionable]:
        """The values selected for a mentionable select menu."""
        mentionables: list[mentionable.Mentionable] = []

        if not self.interaction.resolved:
            return []

        for value in self.interaction.resolved.users.values():
            mentionables.append(mentionable.Mentionable(user=value, role=None))

        for value in self.interaction.resolved.roles.values():
            mentionables.append(mentionable.Mentionable(user=None, role=value))

        return mentionables

    @property
    def channels(self) -> t.Sequence[hikari.PartialChannel]:
        """The values selected for a channel select menu."""
        channels: list[hikari.PartialChannel] = []

        if not self.interaction.resolved:
            return []

        for value in self.interaction.resolved.channels.values():
            channels.append(value)

        return channels

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
