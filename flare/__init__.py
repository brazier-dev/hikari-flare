import importlib.metadata
import typing

from flare.components import *
from flare.context import MessageContext, ModalContext
from flare.converters import Converter, add_converter
from flare.internal.bootstrap import install
from flare.row import Row
from flare.utils import gather_iter

__all__: typing.Sequence[str] = (
    "LinkButton",
    "button",
    "Button",
    "Modal",
    "TextInput",
    "text_select",
    "user_select",
    "role_select",
    "mentionable_select",
    "channel_select",
    "TextSelect",
    "UserSelect",
    "RoleSelect",
    "MentionableSelect",
    "ChannelSelect",
    "MessageContext",
    "ModalContext",
    "Converter",
    "add_converter",
    "install",
    "Row",
    "gather_iter",
)

__version__ = importlib.metadata.version("hikari-flare")

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
