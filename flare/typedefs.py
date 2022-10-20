import typing

if typing.TYPE_CHECKING:
    from flare import Context

ComponentCallbackT = typing.Callable[["Context"], typing.Awaitable[None]]
