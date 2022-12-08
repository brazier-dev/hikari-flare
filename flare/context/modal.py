import typing as t

import hikari

from flare.context.base import PartialContext

__all__: t.Sequence[str] = ("ModalContext",)


class ModalContext(PartialContext[hikari.ModalInteraction]):
    @property
    def components(self) -> t.Sequence[hikari.ModalActionRowComponent]:
        """Returns the components for this modal."""
        return self.interaction.components

    @property
    def values(self) -> t.Sequence[str | None]:
        """Return an array of all `flare.TextInput` selected values."""
        # This is type safe. Not sure why the type checker doesn't understand that.
        return [row[0].value for row in self.components if isinstance(row[0], hikari.TextInputComponent)]  # type: ignore


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
