import dataclasses
import typing

import hikari

Self = typing.TypeVar("Self")


@dataclasses.dataclass
class Context:
    interaction: hikari.ComponentInteraction
    author: hikari.User
