import asyncio
import typing as t

__all__: t.Sequence[str] = ("gather_iter",)


async def gather_iter(iter: t.Iterable[t.Awaitable[t.Any]]):
    return await asyncio.gather(*iter)
