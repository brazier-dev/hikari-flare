import asyncio
import inspect
import typing as t

__all__: t.Sequence[str] = (
    "any_issubclass",
    "gather_iter",
)


def any_issubclass(type: t.Any, base: type) -> bool:
    if not inspect.isclass(type):
        return False
    return issubclass(type, base)


async def gather_iter(iter: t.Iterable[t.Awaitable[t.Any]]):
    return await asyncio.gather(*iter)
