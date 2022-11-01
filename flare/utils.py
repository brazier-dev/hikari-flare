import asyncio
import typing as t

__all__: t.Sequence[str] = ("gather",)


async def gather(iter: t.Iterable[t.Awaitable[t.Any]]):
    return await asyncio.gather(*iter)
