import dataclasses
import hikari
import typing

Self = typing.TypeVar("Self")

@dataclasses.dataclass
class Context:
    interaction: hikari.ComponentInteraction
    author: hikari.User
